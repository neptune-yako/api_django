import dayjs from 'dayjs'

export function formatTime(time, format = 'YYYY-MM-DD HH:mm:ss') {
    if (!time) return '-'
    return dayjs(time).format(format)
}

export function formatDuration(ms) {
    if (!ms) return '0s'
    const seconds = Math.floor(ms / 1000)
    if (seconds < 60) return `${seconds}s`
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}m ${remainingSeconds}s`
}
