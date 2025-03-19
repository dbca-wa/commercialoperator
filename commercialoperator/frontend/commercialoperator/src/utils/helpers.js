module.exports = {
    apiError: function (resp) {
        var error_str = '';
        if (resp.status === 400) {
            try {
                const obj = JSON.parse(resp.responseText);
                error_str = obj.non_field_errors[0].replace(/[[\]"]/g, '');
                // eslint-disable-next-line no-unused-vars
            } catch (e) {
                error_str = resp.responseText.replace(/[[\]"]/g, '');
            }
        } else if (resp.status === 404) {
            error_str = 'The resource you are looking for does not exist.';
        } else {
            error_str = resp.responseText.replace(/[[\]"]/g, '');
        }
        return error_str;
    },
    apiVueResourceError: function (resp) {
        var error_str = '';
        var text = null;

        if (resp.status === 404) {
            return 'The resource you are looking for does not exist.';
        }

        if (resp.status >= 400) {
            if (Array.isArray(resp.body)) {
                text = resp.body[0];
            } else if (typeof resp.body == 'object') {
                text = resp.body;
            } else {
                text = resp.body;
            }

            if (typeof text == 'object') {
                // eslint-disable-next-line no-prototype-builtins
                if (text.hasOwnProperty('non_field_errors')) {
                    error_str = text.non_field_errors[0].replace(/[[\]"]/g, '');
                } else {
                    //error_str = text;

                    for (const key in text) {
                        const element = text[key];
                        if (Array.isArray(element)) {
                            for (let message of element) {
                                error_str = message;
                            }
                        } else {
                            error_str = element;
                        }
                    }
                }
            } else {
                error_str = text.replace(/[[\]"]/g, '');
                error_str = text.replace(/^['"](.*)['"]$/, '$1');
            }
        }

        return error_str;
    },

    goBack: function (vm) {
        vm.$router.go(window.history.back());
    },
    copyObject: function (obj) {
        return JSON.parse(JSON.stringify(obj));
    },
    getCookie: function (name) {
        var value = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (
                    cookie.substring(0, name.length + 1).trim() ===
                    name + '='
                ) {
                    value = decodeURIComponent(
                        cookie.substring(name.length + 1)
                    );
                    break;
                }
            }
        }
        return value;
    },
    namePopover: function ($, vmDataTable) {
        vmDataTable.on('mouseover', '.name_popover', function () {
            $(this).popover('show');
            $(this).on('mouseout', function () {
                $(this).popover('hide');
            });
        });
    },
    add_endpoint_json: function (string, addition) {
        var res = string.split('.json');
        return res[0] + '/' + addition + '.json';
    },
    add_endpoint_join: function (api_string, addition) {
        // assumes api_string has trailing forward slash "/" character required for POST
        return api_string + addition;
    },
    enablePopovers: function () {
        let popoverTriggerList = [].slice.call(
            document.querySelectorAll('[data-bs-toggle="popover"]')
        );
        // eslint-disable-next-line no-unused-vars
        let popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
            // eslint-disable-next-line no-unused-vars
            let popover = new bootstrap.Popover(popoverTriggerEl);
        });
    },
    /**
     * Adds an ellipsis (...) to a string in a datatable cell if it exceeds a certain length
     * @param {String} value The string to truncate
     * @param {String=} title The title of the popover to invoke when the ellipsis is clicked
     * @param {String=} trigger The trigger for the popover to invoke when the ellipsis is clicked
     * @returns The truncated string with an ellipsis and a popover or the original string if it is shorter than the truncation length
     */
    addEllipsis: function (value, title = 'Information', trigger = 'click') {
        var ellipsis = '...',
            truncated = _.truncate(value, {
                length: 25,
                omission: ellipsis,
                separator: ' ',
            }),
            result = '<span>' + truncated + '</span>',
            // prettier-ignore
            popTemplate = _.template(
                '<a href="#" tabindex="0" ' +
                    `data-bs-title="${title} ` +
                    '" ' +
                    'data-bs-template=\'' +
                        '<div class="popover" role="tooltip">' +
                            '<div class="arrow"></div>' +
                            '<div class="row gx-0">' +
                                '<div class="col-10 text-nowrap">' +
                                    '<h3 class="popover-header"></h3>' +
                                '</div>' +
                                '<div class="col-2 text-nowrap close-button-background">' +
                                    '<div type="button" id="close" class="popover-close float-end">' +
                                        '<i class="fa fa-window-close pe-1 pt-1" aria-hidden="true"></i>' +
                                    '</div>' +
                                '</div>' +
                            '</div>' +
                            '<div class="popover-body"></div>' +
                        '</div>\' ' +
                    'role="button" ' +
                    'data-bs-toggle="popover" ' +
                    `data-bs-trigger="${trigger}" ` +
                    'data-bs-placement="top" ' +
                    'data-bs-html="true" ' +
                    // Replace double quotation marks with HTML entities
                    `data-bs-content="<%= text.replace(/"/g, '&quot;') %>" ` +
                `><b>${ellipsis}</b></a>`
            );

        if (_.endsWith(truncated, ellipsis)) {
            result =
                `${truncated.slice(0, -ellipsis.length)}` +
                popTemplate({
                    text: value,
                });
        }

        return result;
    },
    /**
     * Initializes event listeners for ellipsis in a datatable
     * @param {Object} table The datatable object to add the event listeners to
     */
    addEllipsisEventListeners: function (table) {
        //Internal Action shortcut listeners
        table
            .on('draw.dt', function () {
                var popoverTriggerList = [].slice.call(
                    document.querySelectorAll('a[data-bs-toggle="popover"]')
                );
                popoverTriggerList.map(function (popoverTriggerEl) {
                    let popover = new bootstrap.Popover(popoverTriggerEl);
                    // Listeners to hide popovers on 'x'-click
                    table.on(
                        'click',
                        'a[data-bs-toggle="popover"]',
                        function (e) {
                            let attributes = e.currentTarget.attributes;
                            let popoverId;
                            if (attributes && attributes.length > 0) {
                                popoverId =
                                    attributes.getNamedItem(
                                        'aria-describedby'
                                    ).value;
                            }

                            if (popover.tip && popover.tip.id == popoverId) {
                                // Ideally the listener would only be shown on popover show, but that does work okay for now
                                $(`#${popoverId}`)
                                    .find('.popover-close')
                                    .off('click')
                                    .on('click', () => popover.hide());
                            }
                        }
                    );

                    return popover;
                });
            })
            .on('click', function (e) {
                if (['...'].includes(e.target.textContent)) {
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                }
            });
    },
    validateForm: function (form) {
        if (form.checkValidity() === false) {
            form.classList.add('was-validated');
            $(form).find(':invalid').first().focus();
            console.log('Form is invalid');
            return false;
        }
        form.classList.remove('was-validated');

        console.log('Form is valid');
        return true;
    },
    formatABN: function (abn) {
        if (abn.length == 11) {
            return (
                abn.slice(0, 2) +
                ' ' +
                abn.slice(2, 5) +
                ' ' +
                abn.slice(5, 8) +
                ' ' +
                abn.slice(8, 11)
            );
        } else {
            return abn;
        }
    },
    formatACN: function (acn) {
        if (acn.length == 9) {
            return (
                acn.slice(0, 3) + ' ' + acn.slice(3, 6) + ' ' + acn.slice(6, 9)
            );
        } else {
            return acn;
        }
    },
    formatABNorACN: function (input) {
        if (input.length == 11) {
            return this.formatABN(input);
        } else if (input.length == 9) {
            return this.formatACN(input);
        } else {
            return input;
        }
    },
};
