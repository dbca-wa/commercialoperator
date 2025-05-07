<template>
    <div id="internalDash" class="container">
        <!-- Check for true, false, and null to not possibly load both tables while the profile is being fetched -->
        <div v-if="one_row_per_park == true">
            <ParkBookingDash level="internal" />
        </div>
        <div v-else-if="one_row_per_park == false">
            <PaymentDash level="internal" />
        </div>
        <div v-else>
            <i class="fa fa-2x fa-spinner fa-spin"></i>
        </div>
    </div>
</template>
<script>
import ParkBookingDash from '@common-utils/parkbookings_dashboard.vue';
import PaymentDash from '@common-utils/payments_dashboard.vue';
import { api_endpoints } from '@/utils/hooks';
export default {
    name: 'ParkEntryFeesDashboard',
    components: {
        ParkBookingDash,
        PaymentDash,
    },
    data() {
        return {
            profile: {},
            one_row_per_park: null,
        };
    },
    computed: {},
    watch: {},
    mounted: function () {
        this.fetchProfile();
    },
    methods: {
        fetchProfile: function () {
            let vm = this;
            vm.$http.get(api_endpoints.profile).then(
                (response) => {
                    vm.profile = response.body;
                    if (vm.profile.system_settings == null) {
                        vm.one_row_per_park = false;
                    } else {
                        vm.one_row_per_park =
                            vm.profile.system_settings.one_row_per_park;
                    }
                },
                (error) => {
                    console.log(error);
                }
            );
        },
    },
};
</script>
