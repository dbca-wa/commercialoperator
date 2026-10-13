<template lang="html">
    <div id="editEventTrailSection2">
        <modal
            transition="modal fade"
            :title="title"
            large
            @ok="ok()"
            @cancel="cancel()"
        >
            <div class="container-fluid">
                <div class="row">
                    <form
                        ref="parkForm"
                        class="form-horizontal"
                        name="parkForm"
                        novalidate
                        @submit.prevent="ok"
                    >
                        <alert v-if="hasErrors" type="danger"
                            ><strong>{{ errorString }}</strong></alert
                        >
                        <div class="col-sm-12">
                            <!-- Trail Selection -->
                            <div
                                class="form-group"
                                :class="{ 'has-error': errors.events_trail_id }"
                            >
                                <div class="row mb-3">
                                    <div class="col-sm-3">
                                        <label
                                            class="control-label pull-left"
                                            for="events_trail"
                                            >Trail
                                            <span class="text-danger"
                                                >*</span
                                            ></label
                                        >
                                    </div>
                                    <div
                                        id="events_trail_modal"
                                        class="col-sm-9"
                                    >
                                        <select
                                            ref="events_trail"
                                            v-model="events_trail_id"
                                            class="form-select"
                                            :class="{
                                                'is-invalid':
                                                    errors.events_trail_id,
                                            }"
                                            name="event_trail_new"
                                            @change="onTrailChange"
                                        >
                                            <option value="" disabled selected>
                                                Select a Trail
                                            </option>
                                            <option
                                                v-for="t in trails_list"
                                                :key="t.id"
                                                :value="t.id"
                                            >
                                                {{ t.name }}
                                            </option>
                                        </select>
                                        <div
                                            v-if="errors.events_trail_id"
                                            class="invalid-feedback d-block text-start"
                                        >
                                            {{ errors.events_trail_id }}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Section Selection -->
                            <div
                                class="form-group"
                                :class="{ 'has-error': errors.section_id }"
                            >
                                <div class="row mb-3">
                                    <div class="col-sm-3">
                                        <label
                                            class="control-label pull-left"
                                            for="events_section"
                                            >Sections
                                            <span class="text-danger"
                                                >*</span
                                            ></label
                                        >
                                    </div>
                                    <div
                                        id="events_section_modal"
                                        class="col-sm-9"
                                    >
                                        <select
                                            ref="events_section"
                                            v-model="section_id"
                                            class="form-select"
                                            :class="{
                                                'is-invalid': errors.section_id,
                                            }"
                                            name="event_trail_section"
                                            :disabled="!events_trail_id"
                                            @change="errors.section_id = null"
                                        >
                                            <option value="" disabled selected>
                                                Select a Section
                                            </option>
                                            <option
                                                v-for="s in trail_list_filter"
                                                :key="s.id"
                                                :value="s.id"
                                            >
                                                {{ s.name }}
                                            </option>
                                        </select>
                                        <div
                                            v-if="errors.section_id"
                                            class="invalid-feedback d-block text-start"
                                        >
                                            {{ errors.section_id }}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Activity Types -->
                            <div
                                class="form-group"
                                :class="{
                                    'has-error': errors.event_trail_activities,
                                }"
                            >
                                <div class="row mb-3">
                                    <div class="col-sm-3">
                                        <label
                                            class="control-label pull-left"
                                            for="pre_event_name"
                                            >Activity Types
                                            <span
                                                v-if="!is_internal"
                                                class="text-danger"
                                                >*</span
                                            ></label
                                        >
                                    </div>
                                    <div class="col-sm-9">
                                        <input
                                            v-model="
                                                trail.event_trail_activities
                                            "
                                            type="text"
                                            class="form-control"
                                            :class="{
                                                'is-invalid':
                                                    errors.event_trail_activities,
                                            }"
                                            name="pre_event_name"
                                            :readonly="is_internal"
                                            placeholder="Enter one or more activity types"
                                            @input="
                                                errors.event_trail_activities =
                                                    null
                                            "
                                        />
                                        <div
                                            v-if="errors.event_trail_activities"
                                            class="invalid-feedback d-block text-start"
                                        >
                                            {{ errors.event_trail_activities }}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Activity Types (Internal) -->
                            <div v-if="is_internal" class="form-group">
                                <div class="row mb-3">
                                    <div class="col-sm-3">
                                        <label
                                            class="control-label pull-left"
                                            for="trail_activities_select"
                                            >Activity Types (internal)
                                        </label>
                                    </div>
                                    <div
                                        id="trail_activities_select_modal"
                                        class="col-sm-9"
                                    >
                                        <select
                                            ref="trail_activities_select"
                                            v-model="selected_activities"
                                            style="width: 100%"
                                            class="form-control input-sm"
                                            multiple
                                        >
                                            <option
                                                v-for="a in trail_activities"
                                                :key="a.id"
                                                :value="a.id"
                                            >
                                                {{ a.name }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
            <template #footer>
                <button
                    v-if="issuingPark"
                    type="button"
                    disabled
                    class="btn btn-primary"
                    @click="ok"
                >
                    <i class="fas fa-spinner fa-spin"></i> Processing
                </button>
                <button
                    v-else
                    type="button"
                    class="btn btn-primary"
                    @click="ok"
                >
                    Ok
                </button>
                <button type="button" class="btn btn-secondary" @click="cancel">
                    Cancel
                </button>
            </template>
        </modal>
    </div>
</template>

<script>
import modal from '@vue-utils/bootstrap-modal.vue';
import alert from '@vue-utils/alert.vue';
import { helpers, api_endpoints } from '@/utils/hooks.js';
import $ from 'jquery';

export default {
    name: 'EditTrailActivityEvent',
    components: {
        modal,
        alert,
    },
    props: {
        is_internal: {
            type: Boolean,
            default: false,
        },
        trail_action: {
            type: String,
            default: 'edit',
        },
    },
    data: function () {
        return {
            isModalOpen: false,
            trail: {},
            trail_id: null,
            section_id: '',
            events_trail_id: '',
            state: 'proposed_park',
            issuingPark: false,
            trails_list: [],
            section_list: [],
            trail_activities: [],
            selected_activities: [],
            hasErrors: false,
            errorString: '',
            successString: '',
            success: false,
            dateFormat: 'YYYY-MM-DD',
            localTrailAction: JSON.parse(JSON.stringify(this.trail_action)),
            errors: {
                events_trail_id: null,
                section_id: null,
                event_trail_activities: null,
            },
        };
    },
    computed: {
        title: function () {
            return this.localTrailAction === 'add'
                ? 'Add a new Trail'
                : 'Edit a Trail';
        },
        trail_list_filter: function () {
            for (var i = 0; i < this.trails_list.length; i++) {
                if (this.trails_list[i].id == this.events_trail_id) {
                    return this.trails_list[i].sections || [];
                }
            }
            return [];
        },
    },
    watch: {
        trail_action: {
            handler(newVal) {
                this.localTrailAction = JSON.parse(JSON.stringify(newVal));
            },
            deep: true,
        },
    },
    mounted: function () {
        let vm = this;
        vm.fetchAllTrails();
        this.$nextTick(() => {
            vm.eventListeners();
        });
    },
    methods: {
        validateForm: function () {
            this.errors = {
                events_trail_id: null,
                section_id: null,
                event_trail_activities: null,
            };
            let isValid = true;
            let missingFields = [];

            if (!this.events_trail_id) {
                this.errors.events_trail_id = 'Please select a trail.';
                missingFields.push('Trail');
                isValid = false;
            }

            if (!this.section_id) {
                this.errors.section_id = 'Please select a trail section.';
                missingFields.push('Section');
                isValid = false;
            }

            if (!this.is_internal) {
                if (
                    !this.trail.event_trail_activities ||
                    !this.trail.event_trail_activities.trim()
                ) {
                    this.errors.event_trail_activities =
                        'Please enter one or more activity types.';
                    missingFields.push('Activity Types');
                    isValid = false;
                }
            }

            return isValid;
        },
        onTrailChange: function () {
            this.errors.events_trail_id = null;
            this.section_id = '';
            this.fetchSections();
        },
        ok: function () {
            if (this.validateForm()) {
                this.sendData();
            }
        },
        cancel: function () {
            this.close();
        },
        close: function () {
            this.isModalOpen = false;
            this.trail = {};
            this.hasErrors = false;
            this.errorString = '';
            this.errors = {
                events_trail_id: null,
                section_id: null,
                event_trail_activities: null,
            };
            $(this.$refs.trail_activities_select).val(null).trigger('change');
            this.selected_activities = [];
            this.section_list = [];
            this.events_trail_id = '';
            this.section_id = '';
        },
        fetchAllTrails: function () {
            let vm = this;
            helpers.fetchUrl(api_endpoints.event_trail_container).then(
                (response) => {
                    vm.trails_list = response['trails'] || [];
                    vm.trail_activities =
                        response['event_activity_types'] || [];
                },
                (error) => {
                    console.error(error);
                }
            );
        },
        fetchTrail: function (vid) {
            let vm = this;
            helpers
                .fetchUrl(
                    helpers.add_endpoint_json(
                        api_endpoints.proposal_events_trails,
                        vid
                    )
                )
                .then(
                    (res) => {
                        vm.trail = res;
                        if (vm.trail.trail) {
                            vm.events_trail_id = vm.trail.trail.id;
                            vm.fetchSections();
                            if (vm.trail.section) {
                                vm.section_id = vm.trail.section.id;
                            }
                        }
                        if (vm.trail.activities_assessor) {
                            vm.selected_activities =
                                vm.trail.activities_assessor;
                            $(vm.$refs.trail_activities_select)
                                .val(vm.trail.activities_assessor)
                                .trigger('change');
                        }
                    },
                    (err) => {
                        console.error(err);
                    }
                );
        },
        fetchSections: function () {
            let vm = this;
            vm.section_list = [];
            for (var i = 0; i < vm.trails_list.length; i++) {
                if (vm.trails_list[i].id == vm.events_trail_id) {
                    vm.section_list = helpers.copyObject(
                        vm.trails_list[i].sections
                    );
                }
            }
        },
        sendData: function () {
            let vm = this;
            vm.hasErrors = false;
            if (vm.events_trail_id) {
                vm.trail.trail = vm.events_trail_id;
            }
            if (vm.section_id) {
                vm.trail.section = vm.section_id;
            }
            vm.trail.activities_assessor = vm.selected_activities;
            let trail = JSON.parse(JSON.stringify(vm.trail));
            let formData = new FormData();

            formData.append('data', JSON.stringify(trail));
            vm.issuingPark = true;
            if (vm.localTrailAction == 'add' && vm.trail_id == null) {
                helpers
                    .fetchUrl(api_endpoints.proposal_events_trails, {
                        method: 'POST',
                        body: formData,
                    })
                    .then(
                        (response) => {
                            vm.issuingPark = false;
                            vm.trail = {};
                            vm.close();
                            swal.fire({
                                title: 'Created',
                                text: 'New trail record has been created',
                                icon: 'success',
                            });
                            vm.$emit('refreshFromResponse', response);
                        },
                        (error) => {
                            vm.hasErrors = true;
                            vm.issuingPark = false;
                            vm.errorString = helpers.apiVueResourceError(error);
                        }
                    );
            } else {
                helpers
                    .fetchUrl(
                        helpers.add_endpoint_json(
                            api_endpoints.proposal_events_trails,
                            vm.trail_id + '/edit_trail'
                        ),
                        {
                            method: 'POST',
                            body: formData,
                        }
                    )
                    .then(
                        (response) => {
                            vm.issuingPark = false;
                            vm.trail = {};
                            vm.close();
                            swal.fire({
                                title: 'Saved',
                                text: 'Park details has been saved.',
                                icon: 'success',
                            });
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
        eventListeners: function () {
            let vm = this;
            $(vm.$refs.trail_activities_select)
                .select2({
                    theme: 'bootstrap-5',
                    allowClear: true,
                    placeholder: 'Select Activities',
                    dropdownParent: $('#trail_activities_select_modal'),
                })
                .on('select2:select select2:unselect', function (e) {
                    var selected = $(e.currentTarget);
                    vm.selected_activities = selected.val() || [];
                });
        },
    },
};
</script>
