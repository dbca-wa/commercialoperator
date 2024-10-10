<template>
    <div id="internalDash" class="container">
        <FormSection
            :form-collapse="false"
            label="Applications"
            index="applications"
        >
            <ProposalDashTable level="internal" :url="proposals_url" />
        </FormSection>
        <FormSection
            :form-collapse="false"
            label="Applications referred to me"
            index="referrals"
        >
            <ReferralDashTable :url="referrals_url" />
        </FormSection>
        <FormSection
            v-if="is_qaofficer"
            :form-collapse="false"
            label="Applications referred to me for QA"
            index="qa_applications"
        >
            <QAOfficerDashTable
                v-if="is_qaofficer"
                level="internal"
                :url="qaofficer_url"
            />
        </FormSection>
        <FormSection
            :form-collapse="false"
            label="District Applications referred to me"
            index="district_applications"
        >
            <DistrictProposalDashTable
                level="internal"
                :url="district_proposals_url"
            />
        </FormSection>
    </div>
</template>
<script>
import FormSection from '@/components/forms/section_toggle.vue';
import ProposalDashTable from '@common-utils/proposals_dashboard.vue';
import ReferralDashTable from '@common-utils/referrals_dashboard.vue';
import QAOfficerDashTable from '@common-utils/qaofficer_dashboard.vue';
import DistrictProposalDashTable from '@common-utils/district_proposals_dashboard.vue';

import { api_endpoints } from '@/utils/hooks';
export default {
    name: 'ExternalDashboard',
    components: {
        FormSection,
        ProposalDashTable,
        ReferralDashTable,
        QAOfficerDashTable,
        DistrictProposalDashTable,
    },
    data() {
        return {
            proposals_url: api_endpoints.proposals_paginated_internal,
            referrals_url: api_endpoints.referrals_paginated_internal,
            qaofficer_url: api_endpoints.qaofficer_paginated_internal,
            district_proposals_url:
                api_endpoints.district_proposals_paginated_internal,
            is_qaofficer: false,
        };
    },
    computed: {
        dashboard_url: function () {
            return '/api/proposal_paginated/qaofficer_info/';
        },
    },
    watch: {},
    mounted: function () {
        this.check_qaofficer_membership();
    },
    methods: {
        check_qaofficer_membership: function () {
            let vm = this;

            vm.$http.get(vm.dashboard_url).then(
                (response) => {
                    vm.is_qaofficer = response.data['QA_Officer'];
                },
                (error) => {
                    console.log(error);
                }
            );
        },
    },
};
</script>
