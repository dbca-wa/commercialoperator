<template id="proposal_requirements">
    <div>
        <template v-if="isFinalised">
            <div
                v-if="proposal.processing_status == 'Approved'"
                class="col-md-12 alert alert-success"
            >
                <p>
                    The licence has been issued and has been emailed to
                    {{ proposal.applicant }}
                </p>
                <p v-if="proposal.proposed_issuance_approval">
                    Expiry date:
                    {{ proposal.proposed_issuance_approval.expiry_date }}
                </p>
                <p>
                    Licence:
                    <a target="_blank" :href="proposal.permit">licence.pdf</a>
                </p>
            </div>
            <div v-else class="col-md-12 alert alert-warning">
                <p>
                    The application was declined. The decision was emailed to
                    {{ proposal.applicant }}
                </p>
            </div>
        </template>
        <template v-else-if="proposal.processing_status == 'Awaiting Payment'">
            <div class="col-md-12 alert alert-info">
                <p>
                    The licence has been approved, pending payment and an
                    invoice has been emailed to {{ proposal.applicant }}
                </p>
            </div>
        </template>
        <div class="col-md-12">
            <div class="row">
                <div class="panel panel-default">
                    <FormSection
                        :form-collapse="false"
                        :label="!isFinalised ? 'Proposed Decision' : 'Decision'"
                        index="proposed_decision"
                        subtitle=""
                    >
                        <div class="row">
                            <div class="col-sm-12">
                                <template
                                    v-if="!proposal.proposed_decline_status"
                                >
                                    <template v-if="isFinalised">
                                        <div
                                            v-if="
                                                proposal.proposed_issuance_approval
                                            "
                                        >
                                            <p>
                                                <strong>Decision: Issue</strong>
                                            </p>
                                            <p>
                                                <strong
                                                    >Start date:
                                                    {{
                                                        proposal
                                                            .proposed_issuance_approval
                                                            .start_date
                                                    }}</strong
                                                >
                                            </p>
                                            <p>
                                                <strong
                                                    >Expiry date:
                                                    {{
                                                        proposal
                                                            .proposed_issuance_approval
                                                            .expiry_date
                                                    }}</strong
                                                >
                                            </p>
                                            <p>
                                                <strong
                                                    >CC emails:
                                                    {{
                                                        proposal
                                                            .proposed_issuance_approval
                                                            .cc_email
                                                    }}</strong
                                                >
                                            </p>
                                        </div>
                                    </template>
                                    <template v-else>
                                        <p>
                                            <strong
                                                >Proposed decision:
                                                Issue</strong
                                            >
                                        </p>
                                        <p>
                                            <strong
                                                >Proposed start date:
                                                {{
                                                    proposal
                                                        .proposed_issuance_approval
                                                        .start_date
                                                }}</strong
                                            >
                                        </p>
                                        <p>
                                            <strong
                                                >Proposed expiry date:
                                                {{
                                                    proposal
                                                        .proposed_issuance_approval
                                                        .expiry_date
                                                }}</strong
                                            >
                                        </p>
                                        <p>
                                            <strong
                                                >Proposed cc emails:
                                                {{
                                                    proposal
                                                        .proposed_issuance_approval
                                                        .cc_email
                                                }}</strong
                                            >
                                        </p>
                                    </template>
                                </template>
                                <template v-else>
                                    <strong v-if="!isFinalised"
                                        >Proposed decision: Decline</strong
                                    >
                                    <strong v-else>Decision: Decline</strong>
                                </template>
                            </div>
                        </div>
                    </FormSection>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import { api_endpoints, helpers } from '@/utils/hooks';
import FormSection from '@/components/forms/section_toggle.vue';

export default {
    name: 'InternalProposalRequirements',
    components: {
        FormSection,
    },
    props: {
        // eslint-disable-next-line vue/require-default-prop
        proposal: Object,
    },
    data: function () {
        let vm = this;
        return {
            proposedDecision: 'proposal-decision-' + vm._uid,
            proposedLevel: 'proposal-level-' + vm._uid,
            uploadedFile: null,
        };
    },
    computed: {
        hasAssessorMode() {
            return this.proposal.assessor_mode.has_assessor_mode;
        },
        isFinalised: function () {
            return (
                this.proposal.processing_status == 'Approved' ||
                this.proposal.processing_status == 'Declined'
            );
        },
        isApprovalLevel: function () {
            return this.proposal.approval_level != null ? true : false;
        },
    },
    watch: {},
    mounted: function () {},
    methods: {
        readFile: function () {
            let vm = this;
            let _file = null;
            var input = $(vm.$refs.uploadedFile)[0];
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.readAsDataURL(input.files[0]);
                reader.onload = function (e) {
                    _file = e.target.result;
                };
                _file = input.files[0];
            }
            vm.uploadedFile = _file;
            vm.save();
        },
        removeFile: function () {
            let vm = this;
            vm.uploadedFile = null;
            vm.save();
        },
        save: function () {
            let vm = this;
            let data = new FormData(vm.form);
            data.append('approval_level_document', vm.uploadedFile);
            if (vm.proposal.approval_level_document) {
                data.append(
                    'approval_level_document_name',
                    vm.proposal.approval_level_document[0]
                );
            }
            vm.$http
                .post(
                    helpers.add_endpoint_json(
                        api_endpoints.proposals,
                        vm.proposal.id + '/approval_level_document'
                    ),
                    data,
                    {
                        emulateJSON: true,
                    }
                )
                .then(
                    (res) => {
                        vm.proposal = res.body;
                        vm.$emit('refreshFromResponse', res);
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
        uploadedFileName: function () {
            return this.uploadedFile != null ? this.uploadedFile.name : '';
        },
        addRequirement() {
            this.$refs.requirement_detail.isModalOpen = true;
        },
        removeRequirement(_id) {
            let vm = this;
            swal({
                title: 'Remove Requirement',
                text: 'Are you sure you want to remove this requirement?',
                type: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Remove Requirement',
                confirmButtonColor: '#d9534f',
            }).then(
                () => {
                    vm.$http
                        .delete(
                            helpers.add_endpoint_json(
                                api_endpoints.proposal_requirements,
                                _id
                            )
                        )
                        .then(
                            () => {
                                vm.$refs.requirements_datatable.vmDataTable.ajax.reload();
                            },
                            (error) => {
                                console.log(error);
                            }
                        );
                },
                () => {}
            );
        },
    },
};
</script>
<style scoped></style>
