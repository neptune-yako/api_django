import * as echarts from 'echarts'

// 亮色主题配置
const lightTheme = {
    chart1: ['#107dec', '#1ab43a', '#f4b806', '#ef0d25', '#676666'],
    chart2: ['#1ab43a', '#f4b806', '#ef0d25', '#676666'],
    chart3: {
        line: '#19a3df',
        area: ['#0085c7', '#22496f', '#080a0b'],
    },
    bg: '#ffffff',
    text: '#080a0b',
    axisLine: '#262727',
    splitLine: '#262727'
}

// 暗黑主题配置
const darkTheme = {
    chart1: ['#4a90e2', '#32cd32', '#ffd700', '#ff4500', '#a9a9a9'],
    chart2: ['#32cd32', '#ffd700', '#ff4500', '#a9a9a9'],
    chart3: {
        line: '#66ccff',
        area: ['#004466', '#113344', '#001a26'],
    },
    bg: '#080a0b',
    text: '#ffffff',
    axisLine: '#666666',
    splitLine: '#444444'
}
// 主题获取方法
const getTheme = (isDark) => {
    return isDark ? darkTheme : lightTheme
}

export default {
    // bug信息图表（横向柱状图）
    chart1(ele, data, dataLabel, isDark) {
        /*
        ele:显示图表的元素
        data:包含数据的数组 [100，80，13，7]
        dataLabel:包含数据的名称的数组 ['总数','处理完','处理中','未处理','无效的']
        */
        const theme = getTheme(isDark)
        //1.初始化chart01
        const chart1 = echarts.init(ele)
        let barLengths = []
        data.forEach((item) => {
            barLengths.push(data[0])
        })
        //2.配置数据
        // 柱状图颜色数组
        const option = {
            backgroundColor: theme.bg,
            //图标位置
            grid: {
                top: '3%',
                left: '20%',
                bottom: '3%',
                backgroundColor: theme.bg
            },
            xAxis: {
                show: false
            },
            yAxis: [{
                show: true,
                data: dataLabel,
                inverse: true,
                axisLine: {
                    show: false
                },
                splitLine: {
                    show: false
                },
                axisTick: {
                    show: false
                },
                axisLabel: {
                    color: theme.text,
                    fontWeight: 'bold',
                    fontSize: 14
                }
            },
                {
                    show: false,
                    inverse: true,
                    data: data,
                    axisLabel: {
                        fontSize: 12,
                        color: theme.text,
                    },
                    axisTick: {
                        show: false
                    },
                    axisLine: {
                        show: false
                    }
                }
            ],
            series: [{
                type: 'bar',
                yAxisIndex: 0,
                data: data,
                barCategoryGap: 50,
                barWidth: 12,
                itemStyle: {
                    borderRadius: 6,
                    borderColor: theme.bg,
                    color: ({dataIndex}) => theme.chart1[dataIndex % theme.chart1.length],
                    borderWidth: 1
                }
            },
                {
                    type: 'bar',
                    yAxisIndex: 1,
                    barCategoryGap: 50,
                    data: barLengths,
                    barWidth: 16,
                    itemStyle: {
                        color: 'none',
                        borderWidth: 2,
                        borderRadius: 6
                    },
                    label: {
                        show: true,
                        position: 'right',
                        formatter: '{b}条',
                        color: theme.text,
                        fontWeight: 'bold',
                        fontSize: 14
                    }
                }
            ]
        }
        // 渲染图表
        chart1.setOption(option)
        return chart1
    },

    // bug率图表（饼图）
    chart2(ele, datas, isDark) {
        /*
        ele：展示图表的元素
        datas: 通过率数据：格式如下
            [{
                value: 80,
                name: '处理完'
            }, {
                value: 30,
                name: '处理中'
            }, {
                value: 10,
                name: '未处理'
            }, {
                value: 1,
                name: '无效的'
            }]
        */
        const theme = getTheme(isDark)
        //1.初始化chart2
        const chart2 = echarts.init(ele)
        //2 图表样式配置
        // 饼状图颜色
        const option = {
            backgroundColor: theme.bg,
            color: theme.chart2,
            tooltip: {
                trigger: 'item',
                formatter: '{d}%【共{c}条】',
                backgroundColor: theme.bg,
                borderColor: theme.text,
                textStyle: {
                    color: theme.text,
                    fontSize: '16',
                    fontWeight: 'bold'
                }
            },
            legend: {
                orient: 'vertical',
                right: 10,
                bottom: 10,
                textStyle: {
                    color: theme.text,
                    fontWeight: 'bold'
                }
            },
            series: [{
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                label: {
                    show: false,
                    position: 'center'
                },
                emphasis: {
                    label: {
                        show: true,
                        fontSize: '20',
                        fontWeight: 'bold',
                        color: theme.text,
                    }
                },
                labelLine: {
                    show: false,
                    color: theme.text
                },
                data: datas
            }]
        }
        //3、渲染图表
        chart2.setOption(option)
        return chart2
    },

    // 折线图（通过率趋势图）
    chart3(ele, value, label, isDark) {
        /*
        ele：元素
        value:通过率数组[78,80,60,90]
        labal：x轴刻度 ['2024-12-5','2024-12-8','2024-12-8','2024-12-12','2024-12-13']
        */
        const theme = getTheme(isDark)
        //1.初始化chart01
        const chart3 = echarts.init(ele)
        //2.配置数据
        let option = {
            backgroundColor: theme.bg,
            title: {
                text: "计划通过率(%)",
                textStyle: {
                    fontSize: 14,
                    color: theme.text
                }
            },
            grid: {
                top: 40,
                bottom: 20,
                left: 20,
                right: 20,
                containLabel: true
            },
            tooltip: {
                trigger: 'item',
                formatter: '{b} 测试结果：计划通过率为{c}%',
                axisPointer: {
                    lineStyle: {
                        color: {
                            type: 'linear',
                            x: 0,
                            y: 0,
                            x2: 0,
                            y2: 1,
                            colorStops: [{
                                offset: 0,
                                color: 'rgba(255,255,255,0)' // 0% 处的颜色
                            },
                                {
                                    offset: 0.5,
                                    color: 'rgba(255,255,255,1)' // 100% 处的颜色
                                },
                                {
                                    offset: 1,
                                    color: 'rgba(255,255,255,0)' // 100% 处的颜色
                                }
                            ],
                            global: false // 缺省为false
                        }
                    }
                }
            },
            xAxis: [{
                type: 'category',
                boundaryGap: false,
                show: true,
                axisLabel: {
                    show: false,
                },
                // 坐标线x
                axisLine: {
                    lineStyle: {
                        color: theme.axisLine
                    }
                },
                axisTick: {
                    show: false
                },
                data: label
            }],
            yAxis: [{
                show: true,
                boundaryGap: false,
                type: 'value',
                color: theme.axisLine,
                min: 0,
                max: 100,
                splitNumber: 5,
                interval: 20,
                nameTextStyle: {
                    color: theme.axisLine,
                    fontSize: 12,
                    lineHeight: 40
                },
                splitLine: {
                    lineStyle: {
                        color: theme.splitLine,
                        type: 'dotted'
                    }
                },
                // 坐标线y
                axisLine: {
                    show: true,
                    lineStyle: {
                        color: theme.axisLine
                    }
                },
                axisTick: {
                    show: true
                },
                axisLabel: {
                    show: true,
                    color: theme.text
                }
            }],
            series: [{
                name: '通过率',
                type: 'line',
                smooth: true,
                showSymbol: true,
                symbolSize: 8,
                zlevel: 3,
                itemStyle: {
                    color: theme.chart3.line,
                    borderColor: theme.text
                },
                lineStyle: {
                    width: 1,
                    color: theme.chart3.line
                },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(
                        0,
                        0,
                        0,
                        1,
                        [{
                            offset: 0,
                            color: theme.chart3.area[0]
                        },
                            {
                                offset: 0.5,
                                color: theme.chart3.area[1]
                            },
                            {
                                offset: 1,
                                color: theme.chart3.area[2]
                            }
                        ],
                        false
                    )
                },
                data: value
            }]
        }
        //3.传入数据
        chart3.setOption(option)
        return chart3
    },
}