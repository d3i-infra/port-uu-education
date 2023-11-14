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
export var MultipleChoiceQuestion = function (props) {
    var question = props.question, choices = props.choices, id = props.id, parentSetter = props.parentSetter, locale = props.locale;
    var _a = React.useState(''), selectedChoice = _a[0], setSelectedChoice = _a[1];
    var _b = React.useState(Array(choices.length).fill(false)), checkedArray = _b[0], setCheckedArray = _b[1];
    var copy = prepareCopy(locale);
    var handleChoiceSelect = function (choice, index) {
        setSelectedChoice(choice);
        setCheckedArray(Array.from({ length: choices.length }, function (_, i) { return i === index; }));
    };
    var setParentState = function () {
        parentSetter(function (prevState) {
            prevState[id] = selectedChoice;
            return prevState;
        });
    };
    React.useEffect(function () {
        setParentState();
    });
    return (_jsxs("div", __assign({ className: 'p-4' }, { children: [_jsx(Title3, { text: copy.question }), _jsx("ul", __assign({ className: 'mt-4 space-y-1' }, { children: copy.choices.map(function (choice, index) { return (_jsxs("li", { children: [_jsx("label", __assign({ className: 'inline-flex items-center' }, { children: _jsx("input", { type: 'radio', name: "".concat(index, "-").concat(id), value: choice, checked: checkedArray.at(index), onChange: function () { return handleChoiceSelect(choice, index); }, className: 'mr-1 form-radio' }) })), choice] }, index)); }) }))] })));
    function prepareCopy(locale) {
        return {
            choices: choices.map(function (choice) { return Translator.translate(choice, locale); }),
            question: Translator.translate(question, locale)
        };
    }
};
