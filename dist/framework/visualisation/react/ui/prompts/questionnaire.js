var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React from 'react';
import TextBundle from '../../../../text_bundle';
import { PrimaryButton } from '../elements/button';
import { Translator } from '../../../../translator';
import { isPropsUIQuestionMultipleChoice, isPropsUIQuestionMultipleChoiceCheckbox, isPropsUIQuestionOpen } from '../../../../types/elements';
import { MultipleChoiceQuestion } from '../../ui/elements/question_multiple_choice';
import { MultipleChoiceQuestionCheckbox } from '../../ui/elements/question_multiple_choice_checkbox';
import { OpenQuestion } from '../../ui/elements/question_open';
export var Questionnaire = function (props) {
    var questions = props.questions, description = props.description, resolve = props.resolve, locale = props.locale;
    var _a = React.useState({}), answers = _a[0], setAnswers = _a[1];
    var copy = prepareCopy(locale);
    function handleDonate() {
        var value = JSON.stringify(answers);
        resolve === null || resolve === void 0 ? void 0 : resolve({ __type__: 'PayloadJSON', value: value });
    }
    // Still here in case case we need a cancel button click event handler
    // function handleCancel (): void {
    //   resolve?.({ __type__: 'PayloadFalse', value: false })
    // }
    var renderQuestion = function (item) {
        if (isPropsUIQuestionMultipleChoice(item)) {
            return (_jsx("div", { children: _jsx(MultipleChoiceQuestion, __assign({}, item, { locale: locale, parentSetter: setAnswers })) }, item.id));
        }
        if (isPropsUIQuestionMultipleChoiceCheckbox(item)) {
            return (_jsx("div", { children: _jsx(MultipleChoiceQuestionCheckbox, __assign({}, item, { locale: locale, parentSetter: setAnswers })) }, item.id));
        }
        if (isPropsUIQuestionOpen(item)) {
            return (_jsx("div", { children: _jsx(OpenQuestion, __assign({}, item, { locale: locale, parentSetter: setAnswers })) }, item.id));
        }
        else {
            return (_jsx("div", {}));
        }
    };
    var renderQuestions = function () {
        return questions.map(function (item) { return renderQuestion(item); });
    };
    return (_jsxs("div", { children: [_jsx("div", __assign({ className: 'flex-wrap text-bodylarge font-body text-grey1 text-left' }, { children: copy.description })), _jsx("div", { children: renderQuestions() }), _jsx("div", __assign({ className: 'flex flex-row gap-4 mt-4 mb-4' }, { children: _jsx(PrimaryButton, { label: copy.continueLabel, onClick: handleDonate, color: 'bg-success text-white' }) }))] }));
    function prepareCopy(locale) {
        return {
            description: Translator.translate(description, locale),
            continueLabel: Translator.translate(continueLabel, locale)
        };
    }
};
var continueLabel = new TextBundle()
    .add('en', 'Continue')
    .add('nl', 'Verder');
