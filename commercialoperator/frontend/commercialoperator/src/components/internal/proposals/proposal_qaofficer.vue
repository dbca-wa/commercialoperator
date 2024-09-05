<template lang="html">
    <div id="internal-proposal-onhold">
        <modal
            transition="modal fade"
            title="Application With QA Officer"
            large
            @ok="ok()"
            @cancel="cancel()"
        >
            <div class="container-fluid">
                <div class="row">
                    <form class="form-horizontal" name="withqaForm">
                        <alert :show.sync="showError" type="danger"
                            ><strong>{{ errorString }}</strong></alert
                        >
                        <div class="col-sm-12">
                            <div class="row">
                                <div class="col-sm-offset-2 col-sm-8">
                                    <div class="form-group">
                                        <TextArea
                                            id="id_comments"
                                            :proposal_id="proposal_id"
                                            :readonly="readonly"
                                            name="_comments"
                                            label="Comments"
                                        />
                                        <div v-if="is_qaofficer_status">
                                            <FileField
                                                id="id_file"
                                                :document_url="document_url"
                                                :proposal_id="proposal_id"
                                                :is-repeatable="true"
                                                name="qaofficer_file"
                                                label="Add Document"
                                                @refreshFromResponse="
                                                    refreshFromResponse
                                                "
                                            />
                                        </div>
                                        <div v-else>
                                            <FileField
                                                id="id_file"
                                                :document_url="document_url"
                                                :proposal_id="proposal_id"
                                                :is-repeatable="true"
                                                name="assessor_qa_file"
                                                label="Add Document"
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
        </modal>
    </div>
</template>

<script>
import modal from '@vue-utils/bootstrap-modal.vue';
import alert from '@vue-utils/alert.vue';

import TextArea from '@/components/forms/text-area.vue';
import FileField from '@/components/forms/file.vue';

import { helpers, api_endpoints } from '@/utils/hooks.js';
export default {
    // eslint-disable-next-line vue/component-definition-name-casing
    name: 'proposal-qaofficer',
    components: {
        TextArea,
        FileField,
        modal,
        alert,
    },
    props: {
        // eslint-disable-next-line vue/prop-name-casing
        proposal_id: {
            type: Number,
            required: true,
        },
        // eslint-disable-next-line vue/prop-name-casing
        processing_status: {
            type: String,
            required: true,
        },
    },
    data: function () {
        return {
            isModalOpen: false,
            form: null,
            errors: false,
            errorString: '',
            validation_form: null,
            // eslint-disable-next-line vue/no-reserved-keys
            _file: '_file',
            // eslint-disable-next-line vue/no-reserved-keys
            _comments: '_comments',
        };
    },
    computed: {
        showError: function () {
            var vm = this;
            return vm.errors;
        },
        document_url: function () {
            // location on media folder for the docs - to be passed to FileField
            return this.proposal_id
                ? `/api/proposal/${this.proposal_id}/process_qaofficer_document/`
                : '';
        },
        is_qaofficer_status: function () {
            return this.processing_status == 'With QA Officer' ? true : false;
        },
    },
    mounted: function () {
        let vm = this;
        vm.form = document.forms.onholdForm;
        vm.addFormValidations();
        this.$nextTick(() => {
            vm.eventListerners();
        });
    },
    methods: {
        refreshFromResponse: function (document_list) {
            let vm = this;
            vm.document_list = helpers.copyObject(document_list);
        },
        _refreshFromResponse: function (response) {
            let vm = this;
            vm.document_list = helpers.copyObject(response.body);
        },

        save: function () {
            let vm = this;
            var is_with_qaofficer =
                vm.processing_status == 'With QA Officer' ? true : false;
            var form = document.forms.withqaForm;
            var data = {
                with_qaofficer: is_with_qaofficer ? 'False' : 'True', // since wee need to do the reverse
                file_input_name: 'qaofficer_file',
                proposal: vm.proposal_id,
                text: form.elements['_comments'].value, // getting the value from the text-area.vue field
            };
            vm.$http
                .post(
                    helpers.add_endpoint_json(
                        api_endpoints.proposals,
                        vm.proposal_id + '/with_qaofficer'
                    ),
                    data,
                    {
                        emulateJSON: true,
                    }
                )
                .then(
                    (res) => {
                        if (!is_with_qaofficer) {
                            swal(
                                'Send Application to QA Officer',
                                'Send Application to QA Officer',
                                'success'
                            );
                        } else {
                            swal(
                                'Application QA Officer Assessment Completed',
                                'Application QA Officer Assessment Completed',
                                'success'
                            );
                        }

                        vm.proposal = res.body;
                        vm.$router.push({ path: '/internal' }); //Navigate to dashboard after completing the referral
                    },
                    (err) => {
                        swal(
                            'Submit Error',
                            helpers.apiVueResourceError(err),
                            'error'
                        );
                    }
                );
        },
        ok: function () {
            let vm = this;
            if ($(vm.form).valid()) {
                vm.save();
            }
        },
        cancel: function () {
            let vm = this;
            vm.close();
        },
        close: function () {
            this.isModalOpen = false;
            this.amendment = {
                reason: '',
                reason_id: null,
                proposal: this.proposal_id,
            };
            this.errors = false;
            $(this.$refs.reason).val(null).trigger('change');
            $('.has-error').removeClass('has-error');

            this.validation_form.resetForm();
        },
        addFormValidations: function () {},
        eventListerners: function () {},
    },
};
</script>

<style lang="css"></style>
