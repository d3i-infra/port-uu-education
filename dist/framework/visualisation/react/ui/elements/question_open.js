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
import { Translator } from '../../../../translator';
import { Title3 } from './text';
export var OpenQuestion = function (props) {
    var question = props.question, id = props.id, parentSetter = props.parentSetter, locale = props.locale;
    var _a = React.useState(''), userAnswer = _a[0], setUserAnswer = _a[1];
    var copy = prepareCopy(locale);
    var handleInputChange = function (event) {
        setUserAnswer(event.target.value);
    };
    var setParentState = function () {
        parentSetter(function (prevState) {
            prevState[id] = userAnswer;
            return prevState;
        });
    };
    React.useEffect(function () {
        setParentState();
    });
    return (_jsxs("div", __assign({ className: 'p-4' }, { children: [_jsx(Title3, { text: copy.question }), _jsx("input", { type: 'text', value: userAnswer, onChange: handleInputChange, className: 'w-full px-4 py-2 text-gray-700 bg-gray-100 border border-gray-300 rounded-md resize-none h-16' })] })));
    function prepareCopy(locale) {
        return {
            question: Translator.translate(question, locale)
        };
    }
};
