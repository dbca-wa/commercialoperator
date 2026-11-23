<template lang="html">
    <div>
        <div class="form-group">
            <label :id="id" for="label" class="inline">{{ label }}</label>
            <div id="content-editable-table">
                <table class="table table-striped editable-table">
                    <thead v-if="table.thead.length">
                        <tr>
                            <th
                                v-for="(heading, index) in tableHeader"
                                :key="index"
                            >
                                {{ tableHeader[index] }}
                                <span
                                    v-if="
                                        table.thead[index] == 'Same tour group'
                                    "
                                >
                                    <i
                                        class="fas fa-circle-info"
                                        aria-hidden="true"
                                        title="If a tour visits multiple fee-paying parks on the same calendar day, only one entry fee per passenger applies across those parks, regardless of region. Tick this box for another park visit by the same tour group to avoid charging again for passengers already counted that day. Yanchep and Nambung are always charged separately; ticking this box does not reduce their fees or their fees for other parks."
                                        style="cursor: pointer;  color: blue"
                                    ></i>
                                </span>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr
                            v-for="(row, row_idx) in table.tbody"
                            :key="row_idx"
                        >
                            <td
                                v-for="(_, col_idx) in table.thead"
                                :key="col_idx"
                                :set="
                                    row_item_value = rowItem(row_idx, col_idx)
                                "
                                width="30%"
                            >
                                <div
                                    v-if="col_types[col_idx] == 'select'"
                                    id="select_order_table_park_parent"
                                    class="select_order_table_park_parent"
                                >
                                    <select
                                        :id="`select_order_table_park-${row_idx}-${col_idx}`"
                                        :ref="`select_order_table_park-${row_idx}-${col_idx}`"
                                        v-model="row[col_idx]"
                                        class="tbl_input form-control"
                                        :title="
                                            'Adult Price: ' +
                                            row[col_idx] +
                                            ', Child Price: ' +
                                            row[col_idx]
                                        "
                                        :disabled="disabled"
                                        :clearable="false"
                                        :required="!disabled"
                                        @change="
                                            park_change(
                                                row[col_idx],
                                                row,
                                                row_idx
                                            )
                                        "
                                    >
                                        <option
                                            v-for="o in options"
                                            :key="o.value"
                                            :value="o.value"
                                        >
                                            {{ o.label }}
                                        </option>
                                    </select>
                                </div>
                                <template v-if="col_types[col_idx] == 'date'">
                                    <input
                                        :id="'id_arrival_date_' + row_idx"
                                        style="width:100%"
                                        v-model="row[col_idx]"
                                        class="tbl_input form-control"
                                        :type="col_types[col_idx]"
                                        :max="expiry_date"
                                        :min="today()"
                                        :onclick="isClickable"
                                        :disabled="
                                            [undefined, null, ''].includes(
                                                row[0]
                                            ) === true
                                        "
                                        :required="
                                            [undefined, null, ''].includes(
                                                row[0]
                                            ) === false
                                        "
                                        @change="
                                            date_change(
                                                row[col_idx],
                                                row,
                                                row_idx
                                            )
                                        "
                                    />
                                </template>
                                <template
                                    v-if="col_types[col_idx] == 'checkbox'"
                                >
                                    <input
                                        :id="'id_checkbox_' + row_idx"
                                        v-model="row[col_idx]"
                                        class="tbl_input form-check-input"
                                        :type="col_types[col_idx]"
                                        :checkbox="
                                            get_same_tour_group_checkbox(
                                                row_idx
                                            ).checked
                                        "
                                        :title="
                                            tooltip_same_group_tour(
                                                row,
                                                row_idx
                                            )
                                        "
                                        :disabled="
                                            get_same_tour_group_checkbox(
                                                row_idx
                                            ).disabled
                                        "
                                        @change="tour_group_change(row, row_idx)"
                                    />
                                </template>
                                <template
                                    v-if="
                                        col_types[col_idx] == 'text' ||
                                        col_types[col_idx] == 'number'
                                    "
                                >
                                    <input
                                        v-model="row[col_idx]"
                                        :readonly="readonly"
                                        class="tbl_input form-control"
                                        :class="`row-input row-${row_idx}-input`"
                                        :type="col_types[col_idx]"
                                        min="0"
                                        :required="true"
                                        :onclick="isClickable"
                                        :disabled="disabled"
                                        @change="tour_group_change(row, row_idx)"
                                    />
                                </template>
                                <template v-if="col_types[col_idx] == 'total'">
                                    <div class="currencyinput">
                                        <input
                                            v-model="row[col_idx]"
                                            class="tbl_input form-control"
                                            :type="col_types[col_idx]"
                                            min="0"
                                            disabled
                                        />
                                    </div>
                                </template>
                            </td>
                            <td v-if="!readonly">
                                <a
                                    title="Delete row"
                                    :disabled="disabled"
                                    @click="deleteRow(row, row_idx)"
                                >
                                    <i
                                        class="fas fa-trash"
                                        style="cursor: pointer; color: red"
                                    ></i>
                                </a>
                            </td>
                        </tr>

                        <tr>
                            <td colspan="6" align="right">
                                <div><label>Total:</label></div>
                            </td>
                            <td align="left">
                                <div class="currencyinput">
                                    <input
                                        class="tbl_input form-control"
                                        type="total"
                                        min="0"
                                        :value="total_price()"
                                        disabled
                                    />
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <span
                    ><button
                        class="btn btn-primary"
                        type="button"
                        :disabled="disabled"
                        @click="addRow()"
                    >
                        +</button
                    >Add another park and/or date</span
                >
            </div>
        </div>
        <!-- Hidden input field for form submission (by name and value) -->
        <input
            type="hidden"
            class="form-control"
            :name="name"
            :value="localValue"
        />
    </div>
</template>

<script>
import { helpers } from '@/utils/hooks';
import {
    calculateParkEntryFees,
    isSeparateParkEntryFee,
} from './park_entry_fees.js';
import _ from 'lodash';
import $ from 'jquery'
export default {
    components: {},
    filters: {
        price: function (dict, key) {
            return dict[key];
        },
    },
    props: {
        headers: {
            type: String,
            required: true,
        },
        options: {
            type: Array,
            required: true,
        },
        name: {
            type: String,
            default: function () {
                return '';
            },
        },
        label: {
            type: String,
            default: function () {
                return '';
            },
        },
        // eslint-disable-next-line vue/prop-name-casing
        expiry_date: {
            type: String,
            default: function () {
                return '';
            },
        },
        id: {
            type: String,
            default: function () {
                return '';
            },
        },
        isRequired: {
            type: Boolean,
            default: function () {
                return false;
            },
        },
        // eslint-disable-next-line vue/prop-name-casing
        comment_value: {
            type: String,
            default: function () {
                return '';
            },
        },
        disabled: Boolean,
        readonly: Boolean,
        value: {
            type: String,
            default: function () {
                return null;
            },
        },
    },
    data() {
        return {
            idx_park: 0,
            idx_arrival_date: 1,
            idx_same_group_tour: 2,
            idx_adult: 3,
            idx_child: 4,
            idx_free: 5,
            idx_price: 6,
            idx_adult_same_tour: 7, // these are the net number of adults (that must pay admission fee). Required for invoicing
            idx_child_same_tour: 8,
            idx_free_same_tour: 9,

            isClickable: 'return true;',
            selected_park: {
                default: function () {
                    return {
                        value: String,
                        label: String,
                        prices: Object,
                    };
                },
            },
            localValue: JSON.parse(JSON.stringify(this.value)),
            table: {
                thead: [],
                tbody: [],
            },
            same_tour_group_checkbox: [],
        };
    },

    computed: {
        wc_version: function () {
            return this.$root.wc_version;
        },
        tableHeader: function () {
            if (!this.table.thead) {
                return [];
            }
            if (!this.readonly) {
                return [...this.table.thead, ...['Action']];
            }
            return this.table.thead;
        },
        rowItem: {
            get: function () {
                return (row_idx, col_idx) => {
                    return this.table.tbody[row_idx][col_idx];
                };
            },
        },
    },
    watch: {
        options: {
            handler: function () {
                this.$nextTick(() => {
                    this.refresh_same_tour_group_checkboxes();
                    this.calcPrice();
                });
            },
            deep: true,
        },
        value: {
            handler: function (value) {
                this.localValue = value;
            },
            deep: true,
        },
    },
    beforeUpdate() {},
    created: function () {
        let vm = this;
        var value = JSON.parse(vm.value);

        var headers = JSON.parse(vm.headers);
        vm.col_headers = Object.keys(headers);
        vm.col_types = Object.values(headers);

        // setup initial empty row for display
        vm.init_row = vm.reset_row();

        if (value == null) {
            for (let header_item of vm.col_headers) {
                vm.table.thead.push(header_item);
            }
            vm.table.tbody.push(vm.init_row);
        } else {
            for (let header_item of value['thead']) {
                vm.table.thead.push(header_item);
            }
            for (let body_item of value['tbody']) {
                vm.table.tbody.push(body_item);
            }
        }
        for (var i = 0; i < vm.table.tbody.length; i++) {
            vm.same_tour_group_checkbox.push({
                disabled: true,
                checked: false,
            });
        }
    },
    mounted: function () {
        let vm = this;

        vm.updateTableJSON();

        //$('#content-editable-table').on('change', '[type="text"]', function() {
        $('#content-editable-table').on('change', '.tbl_input', function () {
            vm.updateTableJSON();
        });

        $('#content-editable-table').on('click', '.ibtnDel', function () {
            $(this).closest('tr').remove();
        });

        if (vm.isChecked) {
            var input = this.$refs.Checkbox;
            var e = document.createEvent('HTMLEvents');
            e.initEvent('change', true, true);

            /* replacing input.disabled with onclick because disabled checkbox does NOT get posted with form on submit */
            if (vm.readonly) {
                vm.isClickable = 'return false;';
            } else {
                vm.isClickable = 'return true;';
            }
            input.dispatchEvent(e);
        }

        $('#content-editable-table').on(
            'keypress',
            'input[type="date"]',
            function (event) {
                event.preventDefault();
            }
        );

        this.$nextTick(() => {
            vm.table.tbody.forEach((row, row_idx) => {
                // Initialise select2 for each row
                vm.initialiseRowSelect2(row, row_idx);
            });
            vm.refresh_same_tour_group_checkboxes();
            vm.calcPrice();
        });
    },

    updated() {},
    methods: {
        total_price: function () {
            let vm = this;
            var total = 0.0;
            for (var key in vm.table.tbody) {
                total += isNaN(parseFloat(vm.table.tbody[key][vm.idx_price]))
                    ? 0.0
                    : parseFloat(vm.table.tbody[key][vm.idx_price]);
            }
            return total.toFixed(2);
        },

        today: function () {
            var day = new Date();
            var dd = day.getDate();
            var mm = day.getMonth() + 1; //January is 0!
            var yyyy = day.getFullYear();
            if (dd < 10) {
                dd = '0' + dd;
            }
            if (mm < 10) {
                mm = '0' + mm;
            }

            return yyyy + '-' + mm + '-' + dd;
        },
        reset_row: function () {
            var init_row = [];
            var length = this.col_headers.length + 3; // adding 3, for 3 same_tour_group values for number of adults, children and free_of_charge
            for (var i = 0; i < length; i++) {
                init_row.push(i == 2 ? false : '');
            }
            return init_row;
        },
        reset_row_part: function (row) {
            // reset part of the row (from date onwards)
            for (var i = 1; i < row.length; i++) {
                row[i] = '';
            }
            return row;
        },

        reset_row_checkbox: function (row) {
            // reset part of the row (checkbox only)
            row[this.idx_same_group_tour] = '';
            return row;
        },
        updateTableJSON: function () {
            let vm = this;
            vm.tableJSON = JSON.stringify(vm.table);
            vm.localValue = vm.tableJSON;
        },
        addRow: function () {
            let vm = this;
            var newRow = [];
            // var length = vm.table.thead.length + 3; // adding 3, for 3 same_tour_group values for number of adults, children and free_of_charge

            newRow = vm.reset_row();

            vm.table.tbody.push(newRow);
            vm.same_tour_group_checkbox.push({
                disabled: true,
                checked: false,
            });

            vm.updateTableJSON();
            this.$nextTick(() => {
                vm.initialiseRowSelect2(newRow, vm.table.tbody.length - 1);
            });
        },
        deleteRow: function (row, row_idx) {
            let vm = this;

            vm.table.tbody = vm.table.tbody.filter((_, idx) => idx != row_idx);
            vm.same_tour_group_checkbox.splice(row_idx, 1);
            vm.refresh_same_tour_group_checkboxes();
            vm.calcPrice();
        },

        adult_price: function (row) {
            const options = this.options_by_row(row);
            return options?.prices?.adult || 0;
        },
        child_price: function (row) {
            const options = this.options_by_row(row);
            return options?.prices?.child || 0;
        },

        tooltip_same_group_tour: function (row, row_idx) {
            const arrival = row[this.idx_arrival_date];
            if (!arrival) {
                return '';
            }
            if (this.is_separate_fee_park(row)) {
                return `Tick to record this visit as part of the same tour group on ${arrival}. This park is always charged separately.`;
            }
            return `Tick if this visit is part of the same tour group as another park visit on ${arrival}.`;
        },
        disable_same_tour_group_checkbox: function (row, row_idx) {
            const park = this.options_by_row(row);
            const arrival = row[this.idx_arrival_date];
            if (!park || !arrival) {
                return true;
            }
            if (this.is_separate_fee_park(row)) {
                return false;
            }
            const anotherParkOnDate = this.table.tbody.some(
                (otherRow, otherIndex) =>
                    otherIndex !== row_idx &&
                    otherRow[this.idx_arrival_date] === arrival &&
                    this.options_by_row(otherRow)
            );
            const previouslyBookedOnDate = this.options.some(
                (option) =>
                    Object.prototype.hasOwnProperty.call(
                        option.max_group_arrival_by_date || {},
                        arrival
                    )
            );
            return !anotherParkOnDate && !previouslyBookedOnDate;
        },
        park_change: function (selected_park, row, row_idx) {
            let vm = this;
            if ([null, undefined, ''].includes(selected_park) === true) {
                vm.table.tbody[row_idx] = vm.reset_row();
            }
            vm.refresh_same_tour_group_checkboxes();
            vm.calcPrice(row, row_idx);
        },

        tour_group_change: function (row, row_idx) {
            let vm = this;
            vm.refresh_same_tour_group_checkboxes();
            vm.calcPrice(row, row_idx);
        },

        date_change: function (selected_date, row, row_idx) {
            let vm = this;
            if ([null, undefined, ''].includes(selected_date) === true) {
                vm.table.tbody[row_idx] = vm.reset_row_part(
                    vm.table.tbody[row_idx]
                );
            }
            vm.refresh_same_tour_group_checkboxes();
            vm.calcPrice(row, row_idx);
        },
        /**
         * Get the options object by park id for a specific row
         * @param row A row of the table
         */
        options_by_row: function (row) {
            const park_id = row[this.idx_park];
            return this.options.find((option) => option.value == park_id);
        },
        is_separate_fee_park: function (row) {
            return isSeparateParkEntryFee(this.options_by_row(row)?.label);
        },
        refresh_same_tour_group_checkboxes: function () {
            let changed = false;
            this.table.tbody.forEach((row, row_idx) => {
                const checkbox = this.same_tour_group_checkbox[row_idx];
                if (!checkbox) {
                    return;
                }

                const disabled = this.disable_same_tour_group_checkbox(
                    row,
                    row_idx
                );
                checkbox.disabled = disabled;
                checkbox.checked =
                    !disabled && row[this.idx_same_group_tour] === true;

                if (disabled && row[this.idx_same_group_tour] !== false) {
                    row[this.idx_same_group_tour] = false;
                    changed = true;
                }
            });

            if (changed) {
                this.updateTableJSON();
            }
        },
        calcPrice: function (row, row_idx = -1) {
            this.table.tbody = calculateParkEntryFees(
                this.table.tbody,
                this.options
            );
            this.updateTableJSON();

            if (row_idx < 0 || !this.table.tbody[row_idx]) {
                return;
            }

            const inputs = $(`.row-${row_idx}-input`);
            const visitors = inputs
                .map(function () {
                    return $(this).val();
                })
                .get();
            const totalVisitors = _.sum(visitors.map(Number));

            if (totalVisitors === 0) {
                if (visitors.every((visitor) => String(visitor).length > 0)) {
                    inputs.each(function () {
                        this.setCustomValidity(
                            'The numbers must not be all zero!'
                        );
                        this.reportValidity();
                    });
                }
                inputs.prop('required', true);
                return;
            }

            inputs.each(function () {
                if (Number($(this).val()) > 0) {
                    this.setCustomValidity('');
                    $(this).prop('required', true);
                } else {
                    this.setCustomValidity('');
                    $(this).prop('required', false);
                }
            });
        },
        /**
         * Get the same tour group checkbox for a specific row
         * @param row_idx The index of the row
         */
        get_same_tour_group_checkbox: function (row_idx) {
            const checkbox = this.same_tour_group_checkbox[row_idx];
            if (!checkbox) {
                console.error(
                    `Checkbox not found for row index ${row_idx}. Please check the data structure.`
                );
                // Default to unchecked and disabled
                return { checked: false, disabled: true };
            }
            return checkbox;
        },
        initialiseRowSelect2: function (row, row_idx) {
            const vm = this;
            const idx = vm.idx_park;
            helpers.initialiseSelect2
                .bind(this)(
                    `select_order_table_park-${row_idx}-${idx}`,
                    'select_order_table_park_parent',
                    vm.table.tbody[row_idx][idx],
                    'Select a park',
                    true,
                    0,
                    '',
                    '15rem'
                )
                .on('select2:select', function (e) {
                    vm.table.tbody[row_idx][idx] = e.params.data.id;
                    vm.$refs[
                        `select_order_table_park-${row_idx}-${idx}`
                    ][0].dispatchEvent(
                        new Event('change', { target: e.target })
                    );
                })
                .on('select2:unselect', function (e) {
                    vm.table.tbody[row_idx][idx] = '';
                    vm.$refs[
                        `select_order_table_park-${row_idx}-${idx}`
                    ][0].dispatchEvent(
                        new Event('change', { target: e.target })
                    );
                });
        },
    },
};
</script>

<style scoped lang="css">
.container {
    padding: 30px;
    width: 100%;
}

.editable-table input[type='number'] {
    width: 90px;
}

.editable-table input[type='total'] {
    width: 100px;
}

.output {
    white-space: normal;
}

input[id='header'] {
    outline-style: none;
}

div.currencyinput {
    position: relative;
    padding-left: 15px;
}

div.currencyinput:after {
    position: absolute;
    left: 6px;
    top: 2px;
    content: '$';
}
.select_order_table_park_parent {
    display: block;
}
</style>
<!-- Having this rule non-scoped to ensure it takes precedence -->
<style lang="css">
.select2-container--bootstrap-5
    .select2-selection--single
    .select2-selection__rendered {
    display: inline-block;
    padding: 0px 0px 0px 8px !important;
    word-wrap: break-word;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    height: 35px;
    width: calc(90%);
    position: sticky;
}
</style>
