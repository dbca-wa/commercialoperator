<template>
    <div id="internalDash" class="container">
        <ProposalDashTable level="internal" :url="proposals_url" />
        <ReferralDashTable :url="referrals_url" />
        <QAOfficerDashTable
            v-if="is_qaofficer"
            level="internal"
            :url="qaofficer_url"
        />
        <DistrictProposalDashTable
            level="internal"
            :url="district_proposals_url"
        />
    </div>
</template>
<script>
import ProposalDashTable from '@common-utils/proposals_dashboard.vue';
import ReferralDashTable from '@common-utils/referrals_dashboard.vue';
import QAOfficerDashTable from '@common-utils/qaofficer_dashboard.vue';
import DistrictProposalDashTable from '@common-utils/district_proposals_dashboard.vue';

import { api_endpoints } from '@/utils/hooks';
export default {
    name: 'ExternalDashboard',
    components: {
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
