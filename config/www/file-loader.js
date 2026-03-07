// Adjust these params to your needs
const SVG_FOLDER_LOCATION = "/svg"; // SVG 文件在 Web 服务器上的路径，例如 /config/www/svg

// Usage: file:yourSvgName (no file extensions)
const NAMESPACE = "yz";

// --- 改进点: 集中化的常量和回退数据 ---
// Home Assistant Lovelace 图标的默认 viewBox 通常是 32x32
const DEFAULT_VIEWBOX = "0 0 32 32";
// 当图标加载或解析失败时的默认回退路径数据（原代码中的复杂路径）
const FALLBACK_PATH_DATA = "M18.677,15.975 C17.922,16.509 17.489,17.269 17.489,18.059 C17.489,18.881 16.822,19.548 16,19.548 C15.179,19.548 14.512,18.881 14.512,18.059 C14.512,16.29 15.404,14.645 16.957,13.544 C17.399,13.233 17.803,12.605 17.615,11.776 C17.482,11.189 16.996,10.704 16.408,10.571 C15.698,10.409 15.198,10.7 14.964,10.886 C14.567,11.204 14.338,11.677 14.338,12.186 C14.338,13.008 13.672,13.674 12.85,13.674 C12.029,13.674 11.362,13.008 11.362,12.186 C11.362,10.768 11.998,9.446 13.107,8.56 C14.217,7.673 15.661,7.349 17.067,7.667 C18.776,8.056 20.13,9.41 20.519,11.119 C20.941,12.98 20.217,14.886 18.677,15.975 M16,24.5 C15.172,24.5 14.5,23.829 14.5,23 C14.5,22.172 15.172,21.5 16,21.5 C16.828,21.5 17.5,22.172 17.5,23 C17.5,23.829 16.828,24.5 16,24.5 M16,4 C9.372,4 4,9.373 4,16 C4,22.627 9.372,28 16,28 C22.627,28 28,22.627 28,16 C28,9.373 22.627,4 16,4";

// --- 改进点: 简单的内存缓存用于已加载的 SVG 数据 ---
const svgCache = {};

/**
 * 加载并解析本地服务器上的 SVG 文件。
 * 提取第一个 <path> 元素的 'd' 属性和 <svg> 元素的 'viewBox' 属性。
 * 缓存结果以防止冗余的 fetch 请求和解析。
 *
 * @param {string} path - SVG 文件的名称（不带扩展名）。
 * @returns {Promise<{path: string, viewBox: string}>} - 包含路径数据和 viewBox 的对象，
 *                                                       如果发生错误则返回回退数据。
 */
async function loadFile(path) {
    // 改进点: 检查缓存，如果存在则直接返回
    if (svgCache[path]) {
        return svgCache[path];
    }

    // 默认值，如果后续解析失败则使用这些值
    let pathData = FALLBACK_PATH_DATA;
    let viewBox = DEFAULT_VIEWBOX;

    try {
        const response = await fetch(`/local${SVG_FOLDER_LOCATION}/${path}.svg`);

        if (response.ok) {
            const svgString = await response.text();
            // 改进点: 使用 DOMParser 更健壮地解析 SVG 字符串
            const parser = new DOMParser();
            const svgDoc = parser.parseFromString(svgString, "image/svg+xml");

            // 改进点: 从 <svg> 元素中提取 viewBox 属性
            const svgElement = svgDoc.querySelector("svg");
            if (svgElement && svgElement.getAttribute("viewBox")) {
                viewBox = svgElement.getAttribute("viewBox");
            } else {
                console.warn(`[CustomIconsets] Warning: SVG file '${path}.svg' has no 'viewBox' attribute on its <svg> element. Using default viewBox: '${DEFAULT_VIEWBOX}'.`);
            }

            // 改进点: 从第一个 <path> 元素中提取 'd' 属性，并添加健壮性检查
            const pathElement = svgDoc.querySelector("path");
            if (pathElement && pathElement.getAttribute("d")) {
                pathData = pathElement.getAttribute("d");
            } else {
                // 如果 SVG 成功加载但没有找到路径数据，则警告并使用回退路径
                console.warn(`[CustomIconsets] Warning: SVG file '${path}.svg' loaded successfully but no 'd' attribute found in the first <path> element. Falling back to default error path.`);
            }

            const result = { path: pathData, viewBox: viewBox };
            svgCache[path] = result; // 缓存成功的结果
            return result;

        } else {
            // 改进点: 更详细的错误信息
            console.error(`[CustomIconsets] Error loading SVG file '${path}.svg': ${response.status} ${response.statusText}. Falling back to default error icon.`);
            // 已经使用默认值初始化了 pathData 和 viewBox，直接返回即可
            const result = { path: FALLBACK_PATH_DATA, viewBox: DEFAULT_VIEWBOX };
            svgCache[path] = result; // 缓存错误回退结果
            return result;
        }
    } catch (error) {
        // 改进点: 捕获网络或解析错误，并提供详细信息
        console.error(`[CustomIconsets] Network or parsing error for SVG file '${path}.svg':`, error, "Falling back to default error icon.");
        // 已经使用默认值初始化了 pathData 和 viewBox，直接返回即可
        const result = { path: FALLBACK_PATH_DATA, viewBox: DEFAULT_VIEWBOX };
        svgCache[path] = result; // 缓存错误回退结果
        return result;
    }
}

/**
 * 用于 window.customIconsets 的图标获取函数。
 * 这是 Home Assistant (Lovelace) 将调用的函数，用于获取图标数据。
 *
 * @param {string} name - 图标名称 (例如, "my_icon")。
 * @returns {Promise<{path: string, viewBox: string}>} - 包含 SVG 路径和 viewBox 的对象。
 */
async function getIcon(name) {
    return await loadFile(name);
}

// --- 全局注册自定义图标集 ---
// 确保 window.customIconsets 存在，然后注册此图标集。
window.customIconsets = window.customIconsets || {};
window.customIconsets[NAMESPACE] = getIcon;

// 改进点: 初始化时输出信息，方便调试
console.info(`[CustomIconsets] Custom iconset '${NAMESPACE}' initialized. SVG files expected in /local${SVG_FOLDER_LOCATION}/`);
