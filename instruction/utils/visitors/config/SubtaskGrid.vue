<template>
  <div class="w-full mt-6">
    <div ref="slotWrapper" style="display: none;">
      <slot />
    </div>

    <div class="[gridColumnClass, 'grid gap-6']">
      <div
        v-for="(colItems, colIdx) in chunkedItems"
        :key="colIdx"
        class="flex flex-col gap-5"
      >
        <div
          v-for="itemHtml, itemIdx) in colItems"
          :key="itemIdx"
          class="lh-relaxed"
          v-html="itemHtml"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';

const props = defineProps({
  cols: { type: [Number, String], default: 2 },
  flow: { type: String, default: 'row' }
});

const slotWrapper = ref(null);
const items=ref([]);

onMounted(async () => {
  await nextTick();
  if (slotWrapper.value) {
    const listElements = slotWrapper.value.querySelectorAll('li');
    items.value = Array.from(listElements.map(el => el.innerHTML);
  }
});

const gridColumnClass = computed(() => {
  const c = parseInt(props.cols, 10);
  if (c === 1) return 'grid-cols-1';
  if (c === 3) return 'grid-cols-3';
  if (c === 4) return 'grid-cols-4';
  return 'grid-cols-2'
});

const chunkedItems = computed(() => {
  const numCols = parseInt(props.cols, 10);
  const colsArray = Array.from({ length: numCols }, () => []);

  if (!items.value.length) return colsArray;

  if (props.flow === 'row') {
    items.value.forEach((item, idx) => {
      colsArray[idx % numCols].push(item);
    });
  } else {
    const perCol = Math.ceil(items.value.length / numCols);
    for (let i = 0; i < numCols; i++) {
      colsArray[i] = items.value.slice(i * perCol, (i + 1) * perCol);
    }
  }

  return colsArray;
});
</script>
