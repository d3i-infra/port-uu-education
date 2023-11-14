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
var __spreadArray = (this && this.__spreadArray) || function (to, from, pack) {
    if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
        if (ar || !(i in from)) {
            if (!ar) ar = Array.prototype.slice.call(from, 0, i);
            ar[i] = from[i];
        }
    }
    return to.concat(ar || Array.prototype.slice.call(from));
};
import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React from 'react';
import { Translator } from '../../../../translator';
import { Title3 } from './text';
export var MultipleChoiceQuestionCheckbox = function (props) {
    var question = props.question, choices = props.choices, id = props.id, parentSetter = props.parentSetter, locale = props.locale;
    var _a = React.useState([]), selectedChoices = _a[0], setSelectedChoices = _a[1];
    var copy = prepareCopy(locale);
    var setParentState = function () {
        parentSetter(function (prevState) {
            prevState[id] = selectedChoices;
            return prevState;
        });
    };
    React.useEffect(function () {
        setParentState();
    });
    var handleChoiceSelect = function (event) {
        var _a = event.target, value = _a.value, checked = _a.checked;
        if (checked) {
            setSelectedChoices(function (prevSelectedChoices) { return __spreadArray(__spreadArray([], prevSelectedChoices, true), [
                value
            ], false); });
        }
        else {
            setSelectedChoices(function (prevSelectedChoices) {
                return prevSelectedChoices.filter(function (choice) { return choice !== value; });
            });
        }
    };
    return (_jsxs("div", __assign({ className: 'p-4' }, { children: [_jsx(Title3, { text: copy.question }), _jsx("ul", __assign({ className: 'mt-4 space-y-1' }, { children: copy.choices.map(function (choice, index) { return (_jsx("li", { children: _jsxs("label", __assign({ className: 'flex items-center' }, { children: [_jsx("input", { type: 'checkbox', name: 'choice', value: choice, checked: selectedChoices.includes(choice), onChange: handleChoiceSelect, className: 'mr-1 form-checkbox' }), choice] })) }, index)); }) }))] })));
    function prepareCopy(locale) {
        return {
            choices: choices.map(function (choice) { return Translator.translate(choice, locale); }),
            question: Translator.translate(question, locale)
        };
    }
};
