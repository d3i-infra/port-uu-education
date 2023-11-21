import React from 'react'
import { Weak } from '../../../../helpers'
import TextBundle from '../../../../text_bundle'
import { Translator } from '../../../../translator'
import { PropsUIPageSplashScreen } from '../../../../types/pages'
import { ReactFactoryContext } from '../../factory'
import { PrimaryButton } from '../elements/button'
import { CheckBox } from '../elements/check_box'
import { Label, Title1 } from '../elements/text'
import LogoSvg from '../../../../../assets/images/logo.svg'
import { Footer } from './templates/footer'
import { Page } from './templates/page'
import { Sidebar } from './templates/sidebar'
import { Bullet } from '../elements/bullet'

interface Copy {
  title: string
  continueButton: string
  privacyLabel: string
}

type Props = Weak<PropsUIPageSplashScreen> & ReactFactoryContext

function prepareCopy ({ locale }: Props): Copy {
  return {
    title: Translator.translate(title, locale),
    continueButton: Translator.translate(continueButton, locale),
    privacyLabel: Translator.translate(privacyLabel, locale)
  }
}

export const SplashScreen = (props: Props): JSX.Element => {
  const [checked, setChecked] = React.useState<boolean>(false)
  const [waiting, setWaiting] = React.useState<boolean>(false)
  const { title, continueButton, privacyLabel } = prepareCopy(props)
  const { locale, resolve } = props

  function handleContinue (): void {
    if (checked && !waiting) {
      setWaiting(true)
      resolve?.({ __type__: 'PayloadVoid', value: undefined })
    }
  }

  function handleCheck (): void {
    setChecked(true)
  }

  function renderDescription (): JSX.Element {
    if (locale === 'nl') return nlDescription
    return enDescription
  }

  const enDescription: JSX.Element = (
    <>
      <div className='text-bodylarge font-body text-grey1'>
        <div className='mb-4 text-bodylarge font-body text-grey1'>
            You are about to start the process of donating your data to Utrecht University for “Social Research in the Digital Age”. The data that we ask you to donate will be used in the context of this course.
        </div>
        <div className='mb-4 text-bodylarge font-body text-grey1'>
          During this process no data is stored or sent to a server. Data will only be donated and stored when you click the button “Yes, donate” on the page that shows your data.
        </div>
        <div className='mb-6 text-bodylarge font-body text-grey1'>
          By clicking the button “<span className='font-bodybold'>Yes, donate</span>”:
        </div>
        <div className='flex flex-col gap-3 mb-6'>
          <Bullet>
            <div>You fully and voluntarily agree to donate your data for this course.</div>
          </Bullet>
          <Bullet>
            <div>You are aware that the data you donate will be available to your fellow students and the teachers in this course.</div>
          </Bullet>
          <Bullet>
            <div>You are aware that you have the right to withdraw your permission.</div>
          </Bullet>
        </div>
      </div>
    </>
  )

  const nlDescription: JSX.Element = (
    <>
      <div className='text-bodylarge font-body text-grey1'>
        <div className='mb-4 text-bodylarge font-body text-grey1'>
            You are about to start the process of donating your data to Utrecht University for “Social Research in the Digital Age”. The data that we ask you to donate will be used in the context of this course.
        </div>
        <div className='mb-4 text-bodylarge font-body text-grey1'>
          During this process no data is stored or sent to a server. Data will only be donated and stored when you click the button “Yes, donate” on the page that shows your data.
        </div>
        <div className='mb-6 text-bodylarge font-body text-grey1'>
          By clicking the button “<span className='font-bodybold'>Yes, donate</span>”:
        </div>
        <div className='flex flex-col gap-3 mb-6'>
          <Bullet>
            <div>You fully and voluntarily agree to donate your data for this course.</div>
          </Bullet>
          <Bullet>
            <div>You are aware that the data you donate will be available to your fellow students and the teachers in this course.</div>
          </Bullet>
          <Bullet>
            <div>You are aware that you have the right to withdraw your permission.</div>
          </Bullet>
        </div>
      </div>
    </>
  )

  const footer: JSX.Element = <Footer />

  const sidebar: JSX.Element = <Sidebar logo={LogoSvg} />

  const body: JSX.Element = (
    <>
      <Title1 text={title} />
      {renderDescription()}
      <div className='flex flex-col gap-8'>
        <div className='flex flex-row gap-4 items-center'>
          <CheckBox id='0' selected={checked} onSelect={() => handleCheck()} />
          <Label text={privacyLabel} />
        </div>
        <div className={`flex flex-row gap-4 ${checked ? '' : 'opacity-30'}`}>
          <PrimaryButton label={continueButton} onClick={handleContinue} enabled={checked} spinning={waiting} />
        </div>
      </div>
    </>
  )

  return (
    <Page
      body={body}
      sidebar={sidebar}
      footer={footer}
    />
  )
}

const title = new TextBundle()
  .add('en', 'Welcome')
  .add('nl', 'Welkom')

const continueButton = new TextBundle()
  .add('en', 'Start')
  .add('nl', 'Start')

const privacyLabel = new TextBundle()
  .add('en', 'I have read and agree with the above terms.')
  .add('nl', 'Ik heb deze voorwaarden gelezen en ben hiermee akkoord.')
