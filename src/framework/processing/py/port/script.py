import logging
import json
import io

import port.api.props as props
from port.api.commands import (CommandSystemDonate, CommandUIRender)
import port.whatsapp

LOG_STREAM = io.StringIO()

logging.basicConfig(
    #stream=LOG_STREAM,  # comment this line if you want the logs in std out
    level=logging.INFO,  # change to DEBUG for debugging logs
    format="%(asctime)s --- %(name)s --- %(funcName)s --- %(levelname)s --- %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)

LOGGER = logging.getLogger(__name__)

def process(sessionId):
    LOGGER.info("Starting the donation flow")
    yield donate_logs(f"{sessionId}-tracking")

    platforms = ["Whatsapp"]

    subflows = len(platforms)
    steps = 2
    step_percentage = (100/subflows)/steps
    counter = 0
    # progress in %
    progress = 0

    selectedUsername = ""

    for _, platform in enumerate(platforms):

        list_with_consent_form_tables = []
        progress += step_percentage
        counter = counter + 1

        while True:
            promptFile = prompt_file(platform, "application/zip, text/plain")
            fileResult = yield render_donation_page(platform, promptFile, progress)
            if fileResult.__type__ == 'PayloadString':
                LOGGER.info("Valid file payload")
                yield donate_logs(f"{sessionId}-tracking")

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
                yield donate(f"{sessionId}-{platform}-{counter}", consent_result.value)
                LOGGER.info("Data donated: %s %s", platform, counter)
                yield donate_logs(f"{sessionId}-tracking")
            else:
                LOGGER.info("Skipped ater reviewing consent: %s %s", platform, counter)
                yield donate_logs(f"{sessionId}-tracking")

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
        "en": "Whatsapp Group Chat",
        "nl": "Whatsapp Group Chat"
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
