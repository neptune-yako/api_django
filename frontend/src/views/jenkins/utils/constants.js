export const CONNECTION_STATUS_MAP = {
    connected: { type: 'success', label: '已连接' },
    failed: { type: 'danger', label: '失败' },
    unknown: { type: 'info', label: '未知' }
}

export const BUILD_STATUS_MAP = {
    SUCCESS: { type: 'success', label: '成功' },
    FAILURE: { type: 'danger', label: '失败' },
    UNSTABLE: { type: 'warning', label: '不稳定' },
    ABORTED: { type: 'info', label: '已取消' },
    BUILDING: { type: 'primary', label: '构建中' },
    // 处理空值和未知状态
    '': { type: 'info', label: '未构建' },
    null: { type: 'info', label: '未构建' },
    unknown: { type: 'info', label: '未知' }
}
