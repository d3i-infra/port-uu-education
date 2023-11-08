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
import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import * as React from 'react';
import TextBundle from '../../../../text_bundle';
import { Translator } from '../../../../translator';
import { RadioItem } from '../elements/radio_item';
import { PrimaryButton } from '../elements/button';
function prepareCopy(_a) {
    var title = _a.title, description = _a.description, locale = _a.locale;
    return {
        title: Translator.translate(title, locale),
        description: Translator.translate(description, locale),
        continueButton: Translator.translate(continueButtonLabel(), locale)
    };
}
export var RadioInput = function (props) {
    var _a = React.useState(-1), selectedId = _a[0], setSelectedId = _a[1];
    var _b = React.useState(false), waiting = _b[0], setWaiting = _b[1];
    var _c = React.useState(false), checked = _c[0], setChecked = _c[1];
    var items = props.items, resolve = props.resolve;
    var _d = prepareCopy(props), title = _d.title, description = _d.description, continueButton = _d.continueButton;
    function handleSelect(id) {
        setSelectedId(id);
        setChecked(true);
    }
    function handleConfirm() {
        if (!waiting) {
            setWaiting(true);
            var item = items.at(selectedId);
            if (item !== undefined) {
                resolve === null || resolve === void 0 ? void 0 : resolve({ __type__: 'PayloadString', value: item.value });
            }
        }
    }
    function renderItems(items) {
        return items.map(function (item, index) { return _jsx(RadioItem, { onSelect: function () { return handleSelect(index); }, id: index, value: item.value, selected: selectedId === index }, index); });
    }
    return (_jsxs(_Fragment, { children: [_jsx("div", __assign({ className: 'text-title5 font-title5 sm:text-title4 sm:font-title4 lg:text-title3 lg:font-title3 text-grey1' }, { children: title })), _jsx("div", { className: 'mt-8' }), _jsxs("div", __assign({ id: 'select-panel' }, { children: [_jsx("div", __assign({ className: 'flex-wrap text-bodylarge font-body text-grey1 text-left' }, { children: description })), _jsx("div", { className: 'mt-4' }), _jsx("div", { children: _jsx("div", __assign({ id: 'radio-group', className: 'flex flex-col gap-3' }, { children: renderItems(items) })) })] })), _jsx("div", { className: 'mt-8' }), _jsx("div", __assign({ className: "flex flex-row gap-4 ".concat(checked ? '' : 'opacity-30') }, { children: _jsx(PrimaryButton, { label: continueButton, onClick: handleConfirm, enabled: checked, spinning: waiting }) }))] }));
};
var continueButtonLabel = function () {
    return new TextBundle()
        .add('en', 'Continue')
        .add('nl', 'Doorgaan');
};
