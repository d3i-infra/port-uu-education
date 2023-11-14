import logging
import json
import io

import pandas as pd
        
import port.api.props as props
from port.api.commands import (CommandSystemDonate, CommandUIRender)
import port.whatsapp
import port.whatsapp_account_info as whatsapp_account_info

LOG_STREAM = io.StringIO()

logging.basicConfig(
    #stream=LOG_STREAM,  # comment this line if you want the logs in std out
    level=logging.INFO,  # change to DEBUG for debugging logs
    format="%(asctime)s --- %(name)s --- %(funcName)s --- %(levelname)s --- %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)

LOGGER = logging.getLogger(__name__)

def process(session_id):
    LOGGER.info("Starting the donation flow")
    yield donate_logs(f"{session_id}-tracking")

    steps = 5
    step_percentage = 100/steps
    # progress in %
    progress = 0

    # Whatsapp group char parsing as based on previous study
    platform = "Whatsapp Group Chat"
    selectedUsername = ""
    list_with_consent_form_tables = []
    progress += step_percentage

    while True:
        promptFile = prompt_file(platform, "application/zip, text/plain")
        fileResult = yield render_donation_page(platform, promptFile, progress)
        if fileResult.__type__ == 'PayloadString':

            df_with_chats = port.whatsapp.parse_chat(fileResult.value)

            # If data extracted was successful
            if not df_with_chats.empty:

                df_with_chats = port.whatsapp.remove_empty_chats(df_with_chats)
                group_name = port.whatsapp.extract_groupname(df_with_chats)
                list_with_users = port.whatsapp.extract_users(df_with_chats)
                list_with_users = list(set(list_with_users) - set([group_name]))

                if len(list_with_users) < 3:
                    retry_result = yield render_donation_page(platform, retry_group_chat(), progress)
                    if retry_result.__type__ == "PayloadTrue":
                        continue
                    else:
                        break
                # Determine username upon first donation
                if selectedUsername == "":
                    selection = yield prompt_radio_menu(platform, progress, list_with_users)
                    # If user skips during this process, selectedUsername remains equal to ""
                    if selection.__type__ == "PayloadString":
                        selectedUsername = selection.value
                    else:
                        break

                    df_with_chats = port.whatsapp.filter_username(df_with_chats, group_name)
                    df_with_chats = port.whatsapp.anonymize_users(df_with_chats, list_with_users, selectedUsername)
                    anonymized_users_list = [ f"Deelnemer {i + 1}" for i in range(len(list_with_users))]
                    for user_name in anonymized_users_list:
                        list_with_consent_form_tables.append(port.whatsapp.deelnemer_statistics_to_df(df_with_chats, user_name))

                    break

            # If not enter retry flow
            else:
                retry_result = yield render_donation_page(platform, retry_confirmation(platform), progress)
                if retry_result.__type__ == "PayloadTrue":
                    continue
                else:
                    break
        else:
            break

    progress += step_percentage

    # This check should be here to account for the skip button being
    # This button can be pressed at any moment
    if len(list_with_consent_form_tables) > 0: 
        # STEP 2: ask for consent
        prompt = prompt_consent(list_with_consent_form_tables)
        consent_result = yield render_donation_page(platform, prompt, progress)
        if consent_result.__type__ == "PayloadJSON":
            yield donate(platform, consent_result.value)


    # Short Questionnaire
    render_questionnaire_results = yield render_questionnaire(progress)

    if render_questionnaire_results.__type__ == "PayloadJSON":
        yield donate("questionnaire_results", render_questionnaire_results.value)

    # Whatsapp account info processing
    #
    # Note this a copy paste from previous developed studies 
    # Does not look pretty but it vastly improves the development speed
    platform_name, extraction_fun, validation_fun = ("Whatsapp Account Information", extract_whatsapp_account_info, whatsapp_account_info.validate)
    table_list = None
    progress += step_percentage

    # Prompt file extraction loop
    while True:
        promptFile = prompt_file("application/zip, text/plain, application/json", platform_name)
        file_result = yield render_donation_page(platform_name, promptFile, progress)

        if file_result.__type__ == "PayloadString":
            validation = validation_fun(file_result.value)

            # DDP is recognized: Status code zero
            if validation.status_code.id == 0: 
                LOGGER.info("Payload for %s", platform_name)
                table_list = extraction_fun(file_result.value, validation)
                break

            # DDP is not recognized: Different status code
            if validation.status_code.id != 0: 
                retry_result = yield render_donation_page(platform_name, retry_confirmation(platform_name), progress)
                if retry_result.__type__ == "PayloadTrue":
                    continue
                else:
                    break
        else:
            break

    progress += step_percentage

    # Render data on screen
    if table_list is not None:
        # Check if extract something got extracted
        if len(table_list) == 0:
            table_list.append(create_empty_table(platform_name))

        prompt = assemble_tables_into_form(table_list)
        consent_result = yield render_donation_page(platform_name, prompt, progress)

        if consent_result.__type__ == "PayloadJSON":
            yield donate(platform_name, consent_result.value)


    yield render_end_page()




def prompt_radio_menu(platform, progress, list_with_users):

    title = props.Translatable({
        "en": f"",
        "nl": f""
    })
    description = props.Translatable({
        "en": f"Please select your username",
        "nl": f"Selecteer uw gebruikersnaam"
    })
    header = props.PropsUIHeader(props.Translatable({
        "en": "Submit Whatsapp groupchat",
        "nl": "Submit Whatsapp groupchat"
    }))

    radio_input = [{"id": index, "value": username} for index, username in enumerate(list_with_users)]
    body = props.PropsUIPromptRadioInput(title, description, radio_input)
    footer = props.PropsUIFooter(progress)
    page = props.PropsUIPageDonation(platform, header, body, footer)
    return CommandUIRender(page)


def render_end_page():
    page = props.PropsUIPageEnd()
    return CommandUIRender(page)


def render_donation_page(platform, body, progress):
    header = props.PropsUIHeader(props.Translatable({
        "en": f"{platform}",
        "nl": f"{platform}",
    }))

    footer = props.PropsUIFooter(progress)
    page = props.PropsUIPageDonation(platform, header, body, footer)
    return CommandUIRender(page)



def retry_confirmation(platform):
    text = props.Translatable({
        "en": f"Unfortunately, we cannot process your {platform} file. Continue, if you are sure that you selected the right file. Try again to select a different file.",
        "nl": f"Helaas, kunnen we uw {platform} bestand niet verwerken. Weet u zeker dat u het juiste bestand heeft gekozen? Ga dan verder. Probeer opnieuw als u een ander bestand wilt kiezen."
    })
    ok = props.Translatable({
        "en": "Try again",
        "nl": "Probeer opnieuw"
    })
    cancel = props.Translatable({
        "en": "Continue",
        "nl": "Verder"
    })
    return props.PropsUIPromptConfirm(text, ok, cancel)


def retry_group_chat():
    text = props.Translatable({
        "en": f"Oeps we hebben minder dan 3 deelnemers gevonden, probeer opnieuw",
        "nl": f"Oeps we hebben minder dan 3 deelnemers gevonden, probeer opnieuw"
    })
    ok = props.Translatable({
        "en": "Try again",
        "nl": "Probeer opnieuw"
    })
    cancel = props.Translatable({
        "en": "Cancel",
        "nl": "Cancel"
    })
    return props.PropsUIPromptConfirm(text, ok, cancel)


def prompt_file(_, extensions):

    description = props.Translatable({
        "en": f"Please follow the download instructions and choose the file that you stored on your device.",
        "nl": f"Please follow the download instructions and choose the file that you stored on your device."
    })

    return props.PropsUIPromptFileInput(description, extensions)



def prompt_consent(list_with_consent_form_tables):

    table_list = [table for table in list_with_consent_form_tables if table is not None]
    return props.PropsUIPromptConsentForm(table_list, [])


def donate(key, json_string):
    return CommandSystemDonate(key, json_string)


def donate_logs(key):
    log_string = LOG_STREAM.getvalue()  # read the log stream

    if log_string:
        log_data = log_string.split("\n")
    else:
        log_data = ["no logs"]

    return donate(key, json.dumps(log_data))


#################################################################################################################
# Whatsapp account info functions

def create_empty_table(platform_name: str) -> props.PropsUIPromptConsentFormTable:
    """
    Show something in case no data was extracted
    """
    title = props.Translatable({
       "en": "Er ging niks mis, maar we konden niks vinden",
       "nl": "Er ging niks mis, maar we konden niks vinden"
    })
    df = pd.DataFrame(["No data found"], columns=["No data found"])
    table = props.PropsUIPromptConsentFormTable(f"{platform_name}_no_data_found", title, df)
    return table



def assemble_tables_into_form(table_list: list[props.PropsUIPromptConsentFormTable]) -> props.PropsUIPromptConsentForm:
    """
    Assembles all donated data in consent form to be displayed
    """
    return props.PropsUIPromptConsentForm(table_list, [])



def extract_whatsapp_account_info(account_info_zip: str, _) -> list[props.PropsUIPromptConsentFormTable]:
    """
    Main data extraction function
    Assemble all extraction logic here
    """
    tables_to_render = []

    # Extract comments
    df = whatsapp_account_info.ncontacts_ngroups_device_to_df(account_info_zip)
    print(df)
    if not df.empty:
        table_title = props.Translatable({"en": "Whatsapp account information", "nl": "Whatsapp account information"})
        tables = create_consent_form_tables("whatsapp_account_information", table_title, df) 
        tables_to_render.extend(tables)

    print("TABLES_TO_RENDER")
    print(tables_to_render)
    return tables_to_render


def create_consent_form_tables(unique_table_id: str, title: props.Translatable, df: pd.DataFrame) -> list[props.PropsUIPromptConsentFormTable]:
    """
    This function chunks extracted data into tables of 5000 rows that can be renderd on screen
    """
    table = props.PropsUIPromptConsentFormTable(unique_table_id, title, df)
    out = [table]

    return out


#################################################################################################
# Questionnaire functions


# Questionnaire questions
NCONTACTS = props.Translatable({
    "en": "Estimate the number Whatsapp contacts in your contact list (please enter a number)",
    "nl": "Estimate the number Whatsapp contacts in your contact list (please enter a number)",
})

NGROUPS = props.Translatable({
    "en": "Estimate the number Whatsapp groups you are in (please enter a number)",
    "nl": "Estimate the number Whatsapp groups you are in (please enter a number)",
})

PURPOSE_GROUP = props.Translatable({
    "en": " What is the purpose of the Whatsapp group you donated data about?",
    "nl": " What is the purpose of the Whatsapp group you donated data about?",
})

GENDER = props.Translatable({"en": "What is your gender?", "nl": "What is your gender?"})
GENDER_CHOICES = [
    props.Translatable({"en": "Male", "nl": "Male"}),
    props.Translatable({"en": "Female", "nl": "Female"}),
    props.Translatable({"en": "Other", "nl": "Other"}),
    props.Translatable({"en": "Don't want to say", "nl": "Don't want to say"})
]

def render_questionnaire(progress):
    questions = [
        props.PropsUIQuestionMultipleChoice(question=GENDER, id="gender", choices=GENDER_CHOICES),
        props.PropsUIQuestionOpen(question=PURPOSE_GROUP, id="purpose_group"),
        props.PropsUIQuestionOpen(question=NCONTACTS, id="estimated_ncontacts"),
        props.PropsUIQuestionOpen(question=NGROUPS, id="estimated_ngroups"),
    ]

    description = props.Translatable({"en": "", "nl": ""})
    header = props.PropsUIHeader(props.Translatable({"en": "Questionnaire", "nl": "Questionnaire"}))
    body = props.PropsUIPromptQuestionnaire(questions=questions, description=description)
    footer = props.PropsUIFooter(progress)

    page = props.PropsUIPageDonation("questionnaire", header, body, footer)
    return CommandUIRender(page)

