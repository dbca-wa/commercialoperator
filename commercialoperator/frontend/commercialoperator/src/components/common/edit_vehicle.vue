<template lang="html">
    <div id="editVehicle">
        <modal
            transition="modal fade"
            :title="title"
            large
            @ok="ok()"
            @cancel="cancel()"
        >
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="vehicleForm">
                        <alert :show.sync="showError" type="danger"
                            ><strong>{{ errorString }}</strong></alert
                        >
                        <div class="col-sm-12">
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label
                                            class="control-label pull-left"
                                            for="Name"
                                            >Vehicle Type</label
                                        >
                                    </div>
                                    <div class="col-sm-9">
                                        <select
                                            ref="access_type"
                                            v-model="vehicle_access_id"
                                            class="form-control"
                                            name="access_type"
                                        >
                                            <option
                                                v-for="a in access_types"
                                                :key="a.id"
                                                :value="a.id"
                                            >
                                                {{ a.name }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label
                                            class="control-label pull-left"
                                            for="Name"
                                            >Seating Capacity</label
                                        >
                                    </div>
                                    <div class="col-sm-9">
                                        <input
                                            ref="capacity"
                                            v-model="vehicle.capacity"
                                            class="form-control"
                                            name="capacity"
                                            type="text"
                                        />
                                    </div>
                                </div>
                            </div>

                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label
                                            class="control-label pull-left"
                                            for="Name"
                                            >Registration No.</label
                                        >
                                    </div>
                                    <div class="col-sm-9">
                                        <input
                                            ref="rego"
                                            v-model="vehicle.rego"
                                            class="form-control"
                                            name="rego"
                                            type="text"
                                        />
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label
                                            class="control-label pull-left"
                                            for="Name"
                                            >Registration Expiry</label
                                        >
                                    </div>
                                    <div class="col-sm-9">
                                        <div
                                            ref="rego_expiry"
                                            class="input-group date"
                                            style="width: 70%"
                                        >
                                            <input
                                                v-model="vehicle.rego_expiry"
                                                type="date"
                                                class="form-control"
                                                name="rego_expiry"
                                                placeholder="DD/MM/YYYY"
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

                            <div class="form-group">
                                <div class="row">
                                    <div class="col-sm-3">
                                        <label
                                            class="control-label pull-left"
                                            for="Name"
                                            >Transport licence no.</label
                                        >
                                    </div>
                                    <div class="col-sm-9">
                                        <input
                                            ref="license"
                                            v-model="vehicle.license"
                                            class="form-control"
                                            name="license"
                                            type="text"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
            <div slot="footer">
                <button
                    v-if="issuingVehicle"
                    type="button"
                    disabled
                    class="btn btn-default"
                    @click="ok"
                >
                    <i class="fa fa-spinner fa-spin"></i> Processing
                </button>
                <button
                    v-else
                    type="button"
                    class="btn btn-default"
                    @click="ok"
                >
                    Ok
                </button>
                <button type="button" class="btn btn-default" @click="cancel">
                    Cancel
                </button>
            </div>
        </modal>
    </div>
</template>

<script>
import Vue from 'vue';
import modal from '@vue-utils/bootstrap-modal.vue';
import alert from '@vue-utils/alert.vue';
import { helpers, api_endpoints } from '@/utils/hooks.js';
export default {
    // eslint-disable-next-line vue/component-definition-name-casing
    name: 'Edit-Vehicle',
    components: {
        modal,
        alert,
    },
    props: {
        // Note: I'm commenting out the vehicel_id prop because it doesn't seem to be initialized with a non-null value
        // vehicle_id: {
        //     type: Number,
        //     required: true,
        // },
        // eslint-disable-next-line vue/prop-name-casing
        vehicle_action: {
            type: String,
            default: 'edit',
        },
        // eslint-disable-next-line vue/prop-name-casing
        access_types: {
            type: Array,
            required: true,
        },
    },
    data: function () {
        return {
            isModalOpen: false,
            form: null,
            vehicle: Object,
            vehicle_id: Number,
            vehicle_access_id: null,
            state: 'proposed_vehicle',
            issuingVehicle: false,
            validation_form: null,
            hasErrors: false,
            errorString: '',
            successString: '',
            success: false,
            dateFormat: 'YYYY-MM-DD',
            datepickerOptions: {
                format: 'DD/MM/YYYY',
                showClear: true,
                useCurrent: false,
                keepInvalid: true,
                allowInputToggle: true,
            },
            localVehicleAction: JSON.parse(JSON.stringify(this.vehicle_action)),
        };
    },
    computed: {
        showError: function () {
            var vm = this;
            return vm.hasErrors;
        },
        title: function () {
            return this.localVehicleAction == 'add'
                ? 'Add a new Vehicle record'
                : 'Edit a vehicle record';
        },
    },
    watch: {
        vehicle_action: {
            handler(newVal) {
                this.localVehicleAction = JSON.parse(JSON.stringify(newVal));
            },
            deep: true,
        },
    },
    mounted: function () {
        let vm = this;

        vm.form = document.forms.vehicleForm;
        vm.addFormValidations();
        this.$nextTick(() => {
            vm.eventListeners();
        });
    },
    methods: {
        ok: function () {
            let vm = this;
            if ($(vm.form).valid()) {
                vm.sendData();
            }
        },
        cancel: function () {
            this.close();
        },
        close: function () {
            this.isModalOpen = false;
            this.vehicle = {};
            this.hasErrors = false;
            $('.has-error').removeClass('has-error');
            $(this.$refs.rego_expiry).val('');
            this.$refs.capacity = '';
            this.$refs.license = '';
            this.$refs.rego = '';
            this.validation_form.resetForm();
        },
        fetchContact: function (id) {
            let vm = this;
            vm.$http.get(api_endpoints.contact(id)).then(
                (response) => {
                    vm.contact = response.body;
                    vm.isModalOpen = true;
                },
                (error) => {
                    console.log(error);
                }
            );
        },
        fetchVehicle: function (vid) {
            let vm = this;
            Vue.http
                .get(helpers.add_endpoint_json(api_endpoints.vehicles, vid))
                .then(
                    (res) => {
                        vm.vehicle = res.body;
                        if (vm.vehicle.access_type) {
                            vm.vehicle_access_id = vm.vehicle.access_type.id;
                        }
                    },
                    (err) => {
                        console.log(err);
                    }
                );
        },

        sendData: function () {
            let vm = this;
            vm.hasErrors = false;
            if (vm.vehicle_access_id != null) {
                vm.vehicle.access_type = vm.vehicle_access_id;
            }
            let vehicle = JSON.parse(JSON.stringify(vm.vehicle));
            // Format the date to align with the backend
            vehicle['rego_expiry'] = moment(vehicle['rego_expiry']).format(
                'DD/MM/YYYY'
            );
            vm.issuingVehicle = true;
            if (vm.localVehicleAction == 'add' && vm.vehicle_id == null) {
                vm.$http
                    .post(api_endpoints.vehicles, JSON.stringify(vehicle), {
                        emulateJSON: true,
                    })
                    .then(
                        (response) => {
                            vm.issuingVehicle = false;
                            vm.vehicle = {};
                            vm.close();
                            swal.fire({
                                title: 'Created',
                                text: 'New vehicle record has been created.',
                                type: 'success',
                            });
                            vm.$emit('refreshFromResponse', response);
                        },
                        (error) => {
                            vm.hasErrors = true;
                            vm.issuingVehicle = false;
                            vm.errorString = helpers.apiVueResourceError(error);
                        }
                    );
            } else {
                vm.$http
                    .post(
                        helpers.add_endpoint_json(
                            api_endpoints.vehicles,
                            vm.vehicle_id + '/edit_vehicle'
                        ),
                        JSON.stringify(vehicle),
                        {
                            emulateJSON: true,
                        }
                    )
                    .then(
                        (response) => {
                            vm.issuingVehicle = false;
                            vm.vehicle = {};
                            vm.close();
                            swal.fire({
                                title: 'Saved',
                                text: 'Vehicle details has been saved.',
                                type: 'success',
                            });
                            vm.$emit('refreshFromResponse', response);
                        },
                        (error) => {
                            vm.hasErrors = true;
                            vm.issuingVehicle = false;
                            vm.errorString = helpers.apiVueResourceError(error);
                        }
                    );
            }
        },
        addFormValidations: function () {
            let vm = this;
            vm.validation_form = $(vm.form).validate({
                rules: {
                    access_type: 'required',
                },
                messages: {},
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
        eventListeners: function () {},
    },
};
</script>

<style lang="css"></style>
