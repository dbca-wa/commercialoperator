<template>
    <div id="internalDash" class="container">
        <FormSection :form-collapse="false" label="Licences" index="approvals">
            <ApprovalDashTable level="internal" :url="approvals_url" />
        </FormSection>
    </div>
</template>
<script>
import FormSection from '@/components/forms/section_toggle.vue';
import ApprovalDashTable from '@common-utils/approvals_dashboard.vue';
import { api_endpoints } from '@/utils/hooks';
export default {
    name: 'InternalApprovalDashboard',
    components: {
        FormSection,
        ApprovalDashTable,
    },
    data() {
        return {
            approvals_url: api_endpoints.approvals_paginated_external,
        };
    },
    computed: {},
    watch: {},
    mounted: function () {},
    methods: {},
};
</script>
