import {ref} from "vue"

function dateFtt(fmt, date) {
    const o = {
        "M+": date.getMonth() + 1, //月份
        "d+": date.getDate(), //日
        "h+": date.getHours(), //小时
        "m+": date.getMinutes(), //分
        "s+": date.getSeconds(), //秒
        "q+": Math.floor((date.getMonth() + 3) / 3), //季度
        "S": date.getMilliseconds() //毫秒
    }
    if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (date.getFullYear() + "").substr(4 - RegExp.$1.length))
    for (const k in o) if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length === 1)
        ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)))
    return fmt
}

export const useTime = () => {
    const year = ref(0) // 年份
    const month = ref(0) // 月份
    const week = ref("") // 星期几
    const day = ref(0) // 天数
    const hour = ref(0) // 小时
    const minute = ref(0) // 分钟
    const second = ref(0) // 秒
    const nowTime = ref("") // 当前时间
    // 更新时间
    const updateTime = () => {
        const date = new Date()
        year.value = date.getFullYear()
        month.value = date.getMonth() + 1
        week.value = "日一二三四五六".charAt(date.getDay())
        day.value = date.getDate()
        hour.value = (date.getHours() + "")?.padStart(2, "0") || new Intl.NumberFormat(undefined,
            {minimumIntegerDigits: 2}).format(date.getHours())
        minute.value = (date.getMinutes() + "")?.padStart(2, "0") || new Intl.NumberFormat(undefined,
            {minimumIntegerDigits: 2}).format(date.getMinutes())
        second.value = (date.getSeconds() + "")?.padStart(2, "0") || new Intl.NumberFormat(undefined,
            {minimumIntegerDigits: 2}).format(date.getSeconds())
        nowTime.value = `${year.value}年${month.value}月${day.value} ${hour.value}:${minute.value}:${second.value}`
    }
    updateTime()
    return {year, month, day, hour, minute, second, week, nowTime}
}

export default {
    // 格式化日期时间
    rTime(date) {
        return dateFtt('yyyy-MM-dd hh:mm:ss', new Date(date))
    }, // 格式化日期
    rDate(date) {
        return dateFtt('yyyy-MM-dd', new Date(date))
    }
}