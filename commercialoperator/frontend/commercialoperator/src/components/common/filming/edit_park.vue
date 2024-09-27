<template lang="html">
    <div id="editPark">
        <modal
            transition="modal fade"
            :title="title"
            large
            @ok="ok()"
            @cancel="cancel()"
        >
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="parkForm">
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
                                            >Park or Reserve</label
                                        >
                                    </div>
                                    <div class="col-sm-9">
                                        <select
                                            ref="filming_park"
                                            v-model="selected_park_id"
                                            class="form-control"
                                            name="park"
                                        >
                                            <option
                                                v-for="p in all_parks"
                                                :key="p.id"
                                                :value="p.id"
                                            >
                                                {{ p.name }}
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
                                            >Feature or site of Interest</label
                                        >
                                    </div>
                                    <div class="col-sm-9">
                                        <input
                                            ref="feature_of_interest"
                                            v-model="park.feature_of_interest"
                                            class="form-control"
                                            name="feature_of_interest"
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
                                            >From</label
                                        >
                                    </div>
                                    <div class="col-sm-9">
                                        <div
                                            ref="from_date"
                                            class="input-group date"
                                            style="width: 70%"
                                        >
                                            <input
                                                v-model="park.from_date"
                                                type="date"
                                                class="form-control"
                                                name="from_date"
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
                                            >To</label
                                        >
                                    </div>
                                    <div class="col-sm-9">
                                        <div
                                            ref="to_date"
                                            class="input-group date"
                                            style="width: 70%"
                                        >
                                            <input
                                                v-model="park.to_date"
                                                type="date"
                                                class="form-control"
                                                name="to_date"
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
                                        <label class="text-left" for="Name"
                                            >Please attach a detailed itinerary
                                            and maps which outline specific
                                            locations and roads/tracks/trails to
                                            be used
                                        </label>
                                    </div>
                                    <div class="col-sm-9">
                                        <div
                                            ref="add_attachments"
                                            class="input-group date"
                                            style="width: 70%"
                                        >
                                            <FileField2
                                                ref="filefield"
                                                :uploaded_documents="
                                                    park.filming_park_documents
                                                "
                                                :delete_url="delete_url"
                                                :proposal_id="park_id"
                                                :is-repeatable="true"
                                                name="filming_park_file"
                                                @refreshFromResponse="
                                                    refreshFromResponse
                                                "
                                            />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
            <div slot="footer">
                <button
                    v-if="issuingPark"
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
import FileField2 from '@/components/forms/filefield2.vue';
export default {
    // eslint-disable-next-line vue/component-definition-name-casing
    name: 'Edit-Park',
    components: {
        modal,
        alert,
        FileField2,
    },
    props: {
        // Note: I'm commenting out the park_id prop because it doesn't seem to be initialized with a non-null value
        // park_id: {
        //     type: Number,
        //     required: true,
        // },
        // eslint-disable-next-line vue/prop-name-casing
        park_action: {
            type: String,
            default: 'edit',
        },
        // eslint-disable-next-line vue/prop-name-casing
        district_proposal: {
            type: Object,
            default: null,
        },
        // eslint-disable-next-line vue/prop-name-casing
        is_external: {
            type: Boolean,
            default: false,
        },
        canEditActivities: {
            type: Boolean,
            default: true,
        },
    },
    data: function () {
        return {
            isModalOpen: false,
            form: null,
            park: Object,
            park_id: Number,
            state: 'proposed_park',
            issuingPark: false,
            all_parks: [],
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
            selected_park_id: null,
        };
    },
    computed: {
        showError: function () {
            var vm = this;
            return vm.hasErrors;
        },
        title: function () {
            return this.park_action == 'add'
                ? 'Add a new Park or Reserve'
                : 'Edit a Park or Reserve';
        },
        delete_url: function () {
            return this.park_id
                ? '/api/proposal_filming_parks/' +
                      this.park_id +
                      '/delete_document/'
                : '';
        },
    },
    mounted: function () {
        let vm = this;
        if (vm.district_proposal) {
            vm.fetchDistrictParks(vm.district_proposal.district);
        } else {
            vm.fetchAllParks();
        }
        vm.form = document.forms.parkForm;
        vm.addFormValidations();
        this.$nextTick(() => {
            vm.eventListeners();
        });
        vm.park.filming_park_documents = vm.$refs.filefield.uploaded_documents;
    },
    methods: {
        refreshFromResponse: function (updated_docs) {
            this.park.filming_park_documents = updated_docs;
        },
        ok: function () {
            let vm = this;
            if ($(vm.form).valid()) {
                vm.sendData();
                vm.$refs.filefield.reset_files();
            }
        },
        cancel: function () {
            this.close();
            this.$refs.filefield.reset_files();
        },
        close: function () {
            this.isModalOpen = false;
            this.park = {};
            this.$refs.filefield.reset_files();
            this.hasErrors = false;
            $('.has-error').removeClass('has-error');
            $(this.$refs.filming_park).val(null).trigger('change');
            this.$refs.feature_of_interest = '';
            this.$refs.park = '';
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
        fetchLandParks: function () {
            let vm = this;
            vm.$http
                .get(
                    helpers.add_endpoint_json(api_endpoints.parks, 'land_parks')
                )
                .then(
                    (response) => {
                        vm.land_parks = response.body;
                    },
                    (error) => {
                        console.log(error);
                    }
                );
        },
        fetchDistrictLandParks: function (id) {
            let vm = this;
            vm.$http
                .get(
                    helpers.add_endpoint_json(
                        api_endpoints.districts,
                        id + '/land_parks'
                    )
                )
                .then(
                    (response) => {
                        vm.land_parks = response.body;
                    },
                    (error) => {
                        console.log(error);
                    }
                );
        },
        fetchAllParks: function () {
            let vm = this;
            if (vm.is_external) {
                vm.$http
                    .get(
                        helpers.add_endpoint_json(
                            api_endpoints.parks,
                            'filming_parks_external_list'
                        )
                    )
                    .then(
                        (response) => {
                            vm.all_parks = response.body;
                        },
                        (error) => {
                            console.log(error);
                        }
                    );
            } else {
                vm.$http
                    .get(
                        helpers.add_endpoint_json(
                            api_endpoints.parks,
                            'filming_parks_list'
                        )
                    )
                    .then(
                        (response) => {
                            vm.all_parks = response.body;
                        },
                        (error) => {
                            console.log(error);
                        }
                    );
            }
        },

        fetchDistrictParks: function (id) {
            let vm = this;
            vm.$http
                .get(
                    helpers.add_endpoint_json(
                        api_endpoints.districts,
                        id + '/parks'
                    )
                )
                .then(
                    (response) => {
                        vm.all_parks = response.body;
                    },
                    (error) => {
                        console.log(error);
                    }
                );
        },

        fetchPark: function (vid) {
            let vm = this;
            Vue.http
                .get(
                    helpers.add_endpoint_json(
                        api_endpoints.proposal_filming_parks,
                        vid
                    )
                )
                .then(
                    (res) => {
                        vm.park = res.body;
                        if (vm.park.park) {
                            vm.selected_park_id = vm.park.park.id;
                            $(vm.$refs.filming_park)
                                .val(vm.park.park.id)
                                .trigger('change');
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
            if (vm.selected_park_id != null) {
                vm.park.park = vm.selected_park_id;
            }
            let park = JSON.parse(JSON.stringify(vm.park));
            let formData = new FormData();
            var files = vm.$refs.filefield.files;
            $.each(files, function (idx, v) {
                var file = v['file'];
                var filename = v['name'];
                var name = 'file-' + idx;
                formData.append(name, file, filename);
            });
            park.num_files = files.length;
            park.input_name = 'filming_park_doc';

            formData.append('data', JSON.stringify(park));
            vm.issuingPark = true;
            if (vm.park_action == 'add' && vm.park_id == null) {
                vm.$http
                    .post(api_endpoints.proposal_filming_parks, formData, {
                        emulateJSON: true,
                    })
                    .then(
                        (response) => {
                            vm.issuingPark = false;
                            vm.park = {};
                            vm.close();
                            swal(
                                'Created',
                                'New park record has been created.',
                                'success'
                            );
                            vm.$emit('refreshFromResponse', response);
                        },
                        (error) => {
                            vm.hasErrors = true;
                            vm.issuingPark = false;
                            vm.errorString = helpers.apiVueResourceError(error);
                        }
                    );
            } else {
                vm.$http
                    .post(
                        helpers.add_endpoint_json(
                            api_endpoints.proposal_filming_parks,
                            vm.park_id + '/edit_park'
                        ),
                        formData,
                        {
                            emulateJSON: true,
                        }
                    )
                    .then(
                        (response) => {
                            vm.issuingPark = false;
                            vm.park = {};
                            vm.close();
                            swal(
                                'Saved',
                                'Park details has been saved.',
                                'success'
                            );
                            vm.$emit('refreshFromResponse', response);
                        },
                        (error) => {
                            vm.hasErrors = true;
                            vm.issuingPark = false;
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
        eventListeners: function () {
            let vm = this;
            $(vm.$refs.filming_park)
                .select2({
                    theme: 'bootstrap',
                    allowClear: true,
                    placeholder: 'Select Park',
                })
                .on('select2:select', function (e) {
                    var selected = $(e.currentTarget);
                    vm.selected_park_id = selected.val();
                })
                .on('select2:unselect', function (e) {
                    var selected = $(e.currentTarget);
                    vm.selected_park_id = selected.val();
                });
        },
    },
};
</script>

<style lang="css"></style>
