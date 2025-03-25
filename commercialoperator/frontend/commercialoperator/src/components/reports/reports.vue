<template lang="html">
    <div class="container">
        <div id="report-form">
            <form
                id="payments-form"
                method="get"
                action="/ledger/payments/api/report"
            >
                <div class="well">
                    <div class="row">
                        <div class="col-md-12">
                            <h3 style="margin-bottom: 20px">
                                Payments Reports
                            </h3>
                            <div v-show="!region" class="row">
                                <div class="col-md-6">
                                    <div class="form-group">
                                        <label for="">Start Date</label>
                                        <div
                                            id="accountsDateStartPicker"
                                            class="input-group date"
                                        >
                                            <input
                                                v-model="
                                                    accountsDateStartPicker
                                                "
                                                type="date"
                                                class="form-control"
                                                name="start"
                                                placeholder="DD/MM/YYYY"
                                                required
                                            />
                                            <span class="input-group-addon">
                                                <span
                                                    class="glyphicon glyphicon-calendar"
                                                ></span>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="form-group">
                                        <label for="">End Date</label>
                                        <div
                                            id="accountsDateEndPicker"
                                            class="input-group date"
                                        >
                                            <input
                                                v-model="accountsDateEndPicker"
                                                type="date"
                                                class="form-control"
                                                name="end"
                                                placeholder="DD/MM/YYYY"
                                                required
                                            />
                                            <span class="input-group-addon">
                                                <span
                                                    class="glyphicon glyphicon-calendar"
                                                ></span>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="row" style="margin-top: 20px">
                                <div class="col-md-6">
                                    <div class="form-group">
                                        <label for="">Bank Start Date</label>
                                        <div
                                            id="flatDateStartPicker"
                                            class="input-group date"
                                        >
                                            <input
                                                v-model="flatDateStartPicker"
                                                type="date"
                                                class="form-control"
                                                name="banked_start"
                                                placeholder="DD/MM/YYYY"
                                                required
                                            />
                                            <span class="input-group-addon">
                                                <span
                                                    class="glyphicon glyphicon-calendar"
                                                ></span>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="form-group">
                                        <label for="">Bank End Date</label>
                                        <div
                                            id="flatDateEndPicker"
                                            class="input-group date"
                                        >
                                            <input
                                                v-model="flatDateEndPicker"
                                                type="date"
                                                class="form-control"
                                                name="banked_end"
                                                placeholder="DD/MM/YYYY"
                                                required
                                            />
                                            <span class="input-group-addon">
                                                <span
                                                    class="glyphicon glyphicon-calendar"
                                                ></span>
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-sm-6">
                                    <button
                                        class="btn btn-primary pull-left"
                                        @click.prevent="generateByAccount()"
                                    >
                                        Generate Report By Accounts
                                    </button>
                                </div>
                                <div class="col-sm-6 clearfix">
                                    <button
                                        class="btn btn-primary pull-left"
                                        @click.prevent="generateFlatReport()"
                                    >
                                        Generate Report Flat
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </form>
            <div class="well well-sm">
                <div class="row">
                    <div class="col-lg-12">
                        <div class="row">
                            <div class="col-sm-12">
                                <div class="row">
                                    <div class="col-sm-6">
                                        <form ref="booking_settlements_form">
                                            <h3 style="margin-bottom: 20px">
                                                Settlement Report
                                            </h3>
                                            <div class="form-group">
                                                <label for="">Date</label>
                                                <div
                                                    ref="bookingSettlementsDatePicker"
                                                    class="input-group date"
                                                >
                                                    <input
                                                        v-model="
                                                            bookingSettlementsDatePicker
                                                        "
                                                        type="date"
                                                        class="form-control"
                                                        name="booking_settlement_date"
                                                        placeholder="DD/MM/YYYY"
                                                        required
                                                    />
                                                    <span
                                                        class="input-group-addon"
                                                    >
                                                        <span
                                                            class="glyphicon glyphicon-calendar"
                                                        ></span>
                                                    </span>
                                                </div>
                                            </div>
                                            <div class="form-group">
                                                <button
                                                    class="btn btn-primary pull-left"
                                                    @click.prevent="
                                                        getBookingSettlementsReport()
                                                    "
                                                >
                                                    Generate Settlement Report
                                                </button>
                                            </div>
                                        </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <form ref="oracle_form">
                <div class="well well-sm">
                    <div class="row">
                        <div class="col-lg-12">
                            <div class="col-lg-12">
                                <h3 style="margin-bottom: 20px">Oracle Job</h3>
                            </div>
                            <div class="row">
                                <div class="col-lg-12">
                                    <div class="col-sm-6">
                                        <div class="form-group">
                                            <label for="">Date</label>
                                            <div
                                                ref="oracleDatePicker"
                                                class="input-group date"
                                            >
                                                <input
                                                    v-model="oracleDatePicker"
                                                    type="date"
                                                    class="form-control"
                                                    name="oracle_date"
                                                    placeholder="DD/MM/YYYY"
                                                    required
                                                />
                                                <span class="input-group-addon">
                                                    <span
                                                        class="glyphicon glyphicon-calendar"
                                                    ></span>
                                                </span>
                                            </div>
                                        </div>
                                        <div class="form-group">
                                            <button
                                                class="btn btn-primary pull-left"
                                                @click.prevent="runOracleJob()"
                                            >
                                                Run Job
                                            </button>
                                        </div>
                                    </div>
                                    <div class="col-sm-6">
                                        <div class="checkbox">
                                            <label
                                                ><input
                                                    v-model="oracle_override"
                                                    type="checkbox"
                                                    value=""
                                                />Override closed period
                                                check</label
                                            >
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </form>
        </div>
    </div>
</template>

<script>
import { api_endpoints, helpers } from '@/utils/hooks.js';
export default {
    // eslint-disable-next-line vue/multi-word-component-names, vue/component-definition-name-casing
    name: 'reports',
    data: function () {
        return {
            form: null,
            refund_form: null,
            oracle_form: null,
            oracleDatePicker: null,
            booking_settlements_form: null,
            bookings_form: null,
            bookingSettlementsDatePicker: null,
            bookingsDatePicker: null,
            accountsDateStartPicker: null,
            accountsDateEndPicker: null,
            flatDateStartPicker: null,
            flatDateEndPicker: null,
            refundsStartPicker: null,
            refundsEndPicker: null,
            regions: [],
            region: '',
            district: '',
            selected_region: {
                code: '',
                name: '',
                districts: [],
            },
            oracle_override: false,
        };
    },
    watch: {
        region: function () {
            let vm = this;
            vm.district = '';
            if (vm.region) {
                vm.selected_region = vm.regions.find(
                    (r) => r.code == vm.region
                );
            } else {
                vm.selected_region = {
                    code: '',
                    name: '',
                    districts: [],
                };
            }
        },
    },
    mounted: function () {
        let vm = this;
        vm.addEventListeners();
    },
    methods: {
        addEventListeners: function () {
            let vm = this;
            vm.form = $('#payments-form');
            vm.refund_form = $('#refund_form');
            vm.oracle_form = $(vm.$refs.oracle_form);
            vm.booking_settlements_form = $(vm.$refs.booking_settlements_form);
            vm.bookings_form = $(vm.$refs.bookings_form);
            vm.addFormValidations();
            vm.fetchRegions();
        },
        runOracleJob() {
            let vm = this;

            if (vm.oracle_form.valid()) {
                let data = moment(vm.oracleDatePicker).format('DD/MM/YYYY');
                let override = vm.oracle_override ? 'true' : 'false';
                vm.$http
                    .get(
                        '/api/oracle_job?date=' + data + '&override=' + override
                    )
                    .then(
                        () => {
                            swal.fire({
                                icon: 'success',
                                title: 'Job Success',
                                text: 'The oracle job was completed successfully',
                            });
                        },
                        (error) => {
                            swal.fire({
                                icon: 'error',
                                title: 'Oracle Job Error',
                                text: helpers.apiVueResourceError(error),
                            });
                        }
                    );
            }
        },
        getBookingSettlementsReport() {
            let vm = this;

            if (vm.booking_settlements_form.valid()) {
                let data = moment(vm.bookingSettlementsDatePicker).format(
                    'DD/MM/YYYY'
                );
                var url = '/api/reports/booking_settlements?date=' + data;
                window.location.assign(url);
            }
        },
        getBookingsReport() {
            let vm = this;

            if (vm.bookings_form.valid()) {
                let data = moment(vm.bookingsDatePicker).format('DD/MM/YYYY');
                var url = '/api/reports/bookings?date=' + data;
                window.location.assign(url);
            }
        },
        fetchRegions: function () {
            let vm = this;
            $.get('/ledger/payments/api/regions?format=json', function (data) {
                vm.regions = data;
            });
        },
        generateFlatReport: function () {
            let vm = this;
            var values = vm.generateValues();
            if (values) {
                values.flat = false;
                vm.getReport(values);
            }
        },
        generateValues: function () {
            let vm = this;

            if (vm.form.valid()) {
                var values = {
                    system: 'S557',
                    start: vm.region
                        ? moment(vm.flatDateStartPicker).format(
                              'YYYY-MM-DD H:mm:ss'
                          )
                        : moment(vm.accountsDateStartPicker).format(
                              'YYYY-MM-DD H:mm:ss'
                          ),
                    end: vm.region
                        ? moment(vm.flatDateEndPicker).format(
                              'YYYY-MM-DD H:mm:ss'
                          )
                        : moment(vm.accountsDateEndPicker).format(
                              'YYYY-MM-DD H:mm:ss'
                          ),
                    banked_start: moment(vm.flatDateStartPicker).format(
                        'YYYY-MM-DD H:mm:ss'
                    ),
                    banked_end: moment(vm.flatDateEndPicker).format(
                        'YYYY-MM-DD H:mm:ss'
                    ),
                };
                return values;
            }
            return false;
        },
        generateByAccount: function () {
            let vm = this;
            var values = vm.generateValues();
            if (values) {
                values.items = true;
                vm.getReport(values);
            }
        },
        generateRefundReport: function () {
            let vm = this;

            if (vm.refund_form.valid()) {
                var values = {
                    start: moment(vm.refundsStartPicker).format('DD/MM/YYYY'),
                    end: moment(vm.refundsEndPicker).format('DD/MM/YYYY'),
                };
                var url = api_endpoints.booking_refunds + '?' + $.param(values);
                window.location.assign(url);
            } else {
                console.log('invalid form');
            }
        },
        getReport: function (values) {
            var url = '/ledger/payments/api/report?' + $.param(values);
            window.location.assign(url);
        },
        addFormValidations: function () {
            let vm = this;
            vm.form.validate({
                rules: {
                    start: {
                        required: function () {
                            return vm.region.length == 0;
                        },
                    },
                    end: {
                        required: function () {
                            return vm.region.length == 0;
                        },
                    },
                    banked_start: 'required',
                    banked_end: 'required',
                },
                messages: {
                    start: 'Field is required',
                    end: 'Field is required',
                    banked_end: 'Field is required',
                    banked_start: 'Field is required',
                },
                showErrors: function (errorMap, errorList) {
                    $.each(this.validElements(), function (index, element) {
                        var $element = $(element);

                        $element
                            .attr('data-original-title', '')
                            .parents('.form-group')
                            .removeClass('has-error');
                    });

                    // destroy tooltips on valid elements
                    // $('.' + this.settings.validClass).tooltip('destroy');

                    // add or update tooltips
                    for (var i = 0; i < errorList.length; i++) {
                        var error = errorList[i];
                        $(error.element)
                            .tooltip({
                                trigger: 'focus',
                            })
                            .attr('data-original-title', error.message)
                            .parents('.form-group')
                            .addClass('has-error');
                    }
                },
            });
            vm.refund_form.validate({
                rules: {
                    refund_start_date: {
                        required: function () {
                            return vm.region.length == 0;
                        },
                    },
                    refund_end_date: {
                        required: function () {
                            return vm.region.length == 0;
                        },
                    },
                },
                messages: {
                    refund_start_date: 'Field is required',
                    refund_end_date: 'Field is required',
                },
                showErrors: function (errorMap, errorList) {
                    $.each(this.validElements(), function (index, element) {
                        var $element = $(element);

                        $element
                            .attr('data-original-title', '')
                            .parents('.form-group')
                            .removeClass('has-error');
                    });

                    // destroy tooltips on valid elements
                    $('.' + this.settings.validClass).tooltip('destroy');

                    // add or update tooltips
                    for (var i = 0; i < errorList.length; i++) {
                        var error = errorList[i];
                        $(error.element)
                            .tooltip({
                                trigger: 'focus',
                            })
                            .attr('data-original-title', error.message)
                            .parents('.form-group')
                            .addClass('has-error');
                    }
                },
            });
            vm.oracle_form.validate({
                rules: {
                    oracle_date: 'required',
                },
                messages: {
                    oracle_date: 'Field is required',
                },
                showErrors: function (errorMap, errorList) {
                    $.each(this.validElements(), function (index, element) {
                        var $element = $(element);

                        $element
                            .attr('data-original-title', '')
                            .parents('.form-group')
                            .removeClass('has-error');
                    });

                    // destroy tooltips on valid elements
                    $('.' + this.settings.validClass).tooltip('destroy');

                    // add or update tooltips
                    for (var i = 0; i < errorList.length; i++) {
                        var error = errorList[i];
                        $(error.element)
                            .tooltip({
                                trigger: 'focus',
                            })
                            .attr('data-original-title', error.message)
                            .parents('.form-group')
                            .addClass('has-error');
                    }
                },
            });
            vm.booking_settlements_form.validate({
                rules: {
                    booking_settlement_date: 'required',
                },
                messages: {
                    booking_settlement_date: 'Field is required',
                },
                showErrors: function (errorMap, errorList) {
                    $.each(this.validElements(), function (index, element) {
                        var $element = $(element);

                        $element
                            .attr('data-original-title', '')
                            .parents('.form-group')
                            .removeClass('has-error');
                    });

                    // destroy tooltips on valid elements
                    $('.' + this.settings.validClass).tooltip('destroy');

                    // add or update tooltips
                    for (var i = 0; i < errorList.length; i++) {
                        var error = errorList[i];
                        $(error.element)
                            .tooltip({
                                trigger: 'focus',
                            })
                            .attr('data-original-title', error.message)
                            .parents('.form-group')
                            .addClass('has-error');
                    }
                },
            });
            vm.bookings_form.validate({
                rules: {
                    bookings_date: 'required',
                },
                messages: {
                    bookings_date: 'Field is required',
                },
                showErrors: function (errorMap, errorList) {
                    $.each(this.validElements(), function (index, element) {
                        var $element = $(element);

                        $element
                            .attr('data-original-title', '')
                            .parents('.form-group')
                            .removeClass('has-error');
                    });

                    // destroy tooltips on valid elements
                    $('.' + this.settings.validClass).tooltip('destroy');

                    // add or update tooltips
                    for (var i = 0; i < errorList.length; i++) {
                        var error = errorList[i];
                        $(error.element)
                            .tooltip({
                                trigger: 'focus',
                            })
                            .attr('data-original-title', error.message)
                            .parents('.form-group')
                            .addClass('has-error');
                    }
                },
            });
        },
    },
};
</script>

<style lang="css"></style>
