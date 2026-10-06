<template lang="html" :id="id">
    <fieldset class="border rounded p-3 m-3">
        <legend>
            {{ emission_standard.emission_standard_type_value }}
        </legend>
        <div class="form-group">
            <div class="row mb-3">
                <div class="col-sm-3">
                    <label class="control-label pull-right" for="Name"
                        >Attach documents</label
                    >
                </div>
                <div class="col-sm-9">
                    <FileField
                        :id="
                            'emission_standard' +
                            emission_standard.emission_standard_type +
                            proposal_id
                        "
                        ref="emission_standard_file"
                        :proposal_id="proposal_id"
                        :is-repeatable="false"
                        :name="
                            'emission_standard' +
                            emission_standard.emission_standard_type
                        "
                        :readonly="!canEditActivities"
                    ></FileField>
                </div>
            </div>
            <div class="row">
                <div class="col-sm-3">
                    <label class="control-label pull-right" for="Name"
                        >Details</label
                    >
                </div>
                <div class="col-sm-9">
                    <div ref="emission_comments" class="" style="width: 70%">
                        <textarea
                            v-model="emission_standard.emission_comments"
                            class="form-control"
                            name="emission_standard_comments"
                            :disabled="readonly"
                        ></textarea>
                    </div>
                </div>
            </div>
        </div>
    </fieldset>
</template>

<script>
import FileField from '@/components/forms/filefield.vue';

export default {
    name: 'EmissionStandard',
    components: {
        FileField,
    },
    props: {
        proposal_id: null,
        emission_standard: {
            type: Object,
            required: true,
        },
        id: String,
        assessor_readonly: Boolean,
        assessorMode: {
            default: function () {
                return false;
            },
        },
        value: {
            default: function () {
                return null;
            },
        },
        readonly: Boolean,
        canEditActivities: {
            type: Boolean,
            default: true,
        },
    },
    data: function () {
        return {
            repeat: 1,
            datepickerOptions: {
                format: 'DD/MM/YYYY',
                showClear: true,
                useCurrent: false,
                keepInvalid: true,
                allowInputToggle: true,
            },
        };
    },
};
</script>
