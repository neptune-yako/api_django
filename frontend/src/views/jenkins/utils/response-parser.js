/**
 * 解析列表响应数据
 * 兼容 Django REST Framework 的分页格式 ({ count: ..., results: [] }) 和普通数组格式
 * @param {Object|Array} response - API 响应数据
 * @returns {Array} - 解析后的数组
 */
export function parseList(response) {
    if (!response) {
        return []
    }

    // 1. 解包 Axios 响应对象
    let data = response.data || response

    // 2. 解包后端 R 统一响应结构 (如果包含 code 和 data 字段)
    // 结构: { code: 200, data: { ... } }
    if (data && data.code !== undefined && data.data !== undefined) {
        data = data.data
    }

    // 3. 如果此刻 data 为 null/undefined (例如 data: null)
    if (!data) {
        return []
    }

    // 4. 如果是数组，直接返回
    if (Array.isArray(data)) {
        return data
    }

    // 5. 如果是 DRF 分页结构 { count: 10, results: [...] }
    if (data.results && Array.isArray(data.results)) {
        return data.results
    }

    // 6. 兜底
    console.warn('Unknown response format:', response)
    return []
}

/**
 * 解析分页信息
 * @param {Object} response - API 响应对象
 * @returns {Object|null} 分页信息 { total, page, pageSize } 或 null
 */
export function parsePagination(response) {
    if (!response) {
        return null
    }

    // 1. 解包 Axios 响应对象
    let data = response.data || response

    // 2. 解包后端 R 统一响应结构
    if (data && data.code !== undefined && data.data !== undefined) {
        data = data.data
    }

    // 3. DRF 分页格式
    if (data && data.count !== undefined) {
        return {
            total: data.count,
            page: data.current || 1,
            pageSize: data.page_size || 20
        }
    }

    // 4. 自定义分页格式
    if (data && data.pagination) {
        return {
            total: data.pagination.total,
            page: data.pagination.page,
            pageSize: data.pagination.page_size
        }
    }

    // 5. 无分页信息
    return null
}

/**
 * 解析总数
 * @param {Object} response 
 * @returns {Number}
 */
export function parseTotal(response) {
    const data = response.data || response
    return data.count || 0
}
