<template>
  <AppLayout>
    <RoadDamageDetection />
  </AppLayout>
</template>

<script>
import AppLayout from "@/components/AppLayout.vue";
import RoadDamageDetection from "@/components/RoadDamageDetection.vue";

export default {
  name: "RoadDetectionPage",
  components: {
    AppLayout,
    RoadDamageDetection,
  },
};
</script>
