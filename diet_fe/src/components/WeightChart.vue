<template>
  <div class="chart-wrap">
    <div v-if="loading" class="chart-placeholder">
      <el-skeleton :rows="6" animated />
    </div>
    <div v-else-if="!records.length" class="chart-empty">
      <el-empty description="暂无数据，快去记录体重吧" />
    </div>
    <v-chart v-else class="echart" :option="chartOption" autoresize />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  DataZoomComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import dayjs from 'dayjs'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, DataZoomComponent])

const props = defineProps({
  records: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const chartOption = computed(() => {
  const sorted = [...props.records].sort((a, b) =>
    dayjs(a.recorded_at).valueOf() - dayjs(b.recorded_at).valueOf(),
  )

  const dates = sorted.map((r) => dayjs(r.recorded_at).format('MM-DD'))
  const weights = sorted.map((r) => r.weight_kg)

  return {
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const p = params[0]
        const r = sorted[p.dataIndex]
        return `${dayjs(r.recorded_at).format('YYYY-MM-DD')}<br/><b>${p.value} kg</b>`
      },
    },
    grid: {
      left: '12%',
      right: '5%',
      top: '12%',
      bottom: weights.length > 10 ? '18%' : '10%',
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: dates.length > 10 ? 45 : 0,
        fontSize: 11,
      },
    },
    yAxis: {
      type: 'value',
      name: '体重 (kg)',
      nameTextStyle: { fontSize: 11 },
      axisLabel: {
        formatter: '{value} kg',
        fontSize: 11,
      },
      splitLine: { lineStyle: { type: 'dashed' } },
    },
    dataZoom:
      weights.length > 14
        ? [
            {
              type: 'inside',
              start: Math.max(0, 100 - Math.round((14 / weights.length) * 100)),
              end: 100,
            },
            { type: 'slider', bottom: 4, height: 20 },
          ]
        : [],
    series: [
      {
        name: '体重',
        type: 'line',
        data: weights,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width: 2, color: '#409eff' },
        itemStyle: { color: '#409eff' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(64,158,255,0.3)' },
              { offset: 1, color: 'rgba(64,158,255,0.02)' },
            ],
          },
        },
      },
    ],
  }
})
</script>

<style scoped>
.chart-wrap {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  min-height: 360px;
  display: flex;
  flex-direction: column;
}

.chart-placeholder,
.chart-empty {
  flex: 1;
  padding: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.echart {
  flex: 1;
  min-height: 360px;
}
</style>
