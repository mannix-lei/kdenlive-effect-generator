// 全局变量
let currentStyle = null;
let currentEffect = null;
let effectModal = null;
let progressModal = null;
let demosModal = null;
let allDemos = [];

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing...');
    
    // 初始化模态框
    try {
        effectModal = new bootstrap.Modal(document.getElementById('effectModal'));
        progressModal = new bootstrap.Modal(document.getElementById('progressModal'));
        
        console.log('Modals initialized successfully');
    } catch (error) {
        console.error('Error initializing modals:', error);
    }
    
    // 加载数据
    loadStyles();
    
    // 绑定事件
    document.getElementById('generateForm').addEventListener('submit', handleGenerateSubmit);
});

// 加载风格列表
async function loadStyles() {
    try {
        const response = await fetch('/api/styles');
        const styles = await response.json();
        
        const stylesList = document.getElementById('stylesList');
        stylesList.innerHTML = '';
        
        styles.forEach(style => {
            const icon = getStyleIcon(style.name);
            const item = document.createElement('a');
            item.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';
            item.href = '#';
            item.onclick = () => selectStyle(style.name);
            
            item.innerHTML = `
                <div>
                    <i class="${icon} style-icon"></i>
                    <span>${getStyleDisplayName(style.name)}</span>
                </div>
                <div>
                    <span class="badge bg-primary stat-badge me-1">${style.effect_count}</span>
                    <span class="badge bg-success stat-badge">${style.preview_count}</span>
                </div>
            `;
            
            stylesList.appendChild(item);
        });
    } catch (error) {
        console.error('Failed to load styles:', error);
        showAlert('加载风格列表失败', 'danger');
    }
}

// 选择风格
async function selectStyle(styleName) {
    currentStyle = styleName;
    
    // 更新选中状态
    document.querySelectorAll('#stylesList .list-group-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.closest('.list-group-item').classList.add('active');
    
    // 更新标题
    document.getElementById('effectsTitle').innerHTML = 
        `<i class="fas fa-film"></i> ${getStyleDisplayName(styleName)} 特效`;
    
    // 加载特效列表
    await loadEffects(styleName);
}

// 加载特效列表
async function loadEffects(styleName) {
    try {
        console.log('loadEffects: Starting to load effects for style:', styleName);
        showLoading('正在加载特效列表...');
        
        console.log(`Loading effects for style: ${styleName}`);
        const response = await fetch(`/api/effects/${styleName}`);
        console.log(`API response status: ${response.status}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const effects = await response.json();
        console.log(`Loaded ${effects.length} effects:`, effects);
        
        const effectsGrid = document.getElementById('effectsGrid');
        effectsGrid.innerHTML = '';
        
        if (effects.length === 0) {
            effectsGrid.innerHTML = `
                <div class="col-12 text-center text-muted py-5">
                    <i class="fas fa-exclamation-circle fa-3x mb-3"></i>
                    <p>该风格下暂无特效</p>
                    <button class="btn btn-primary" onclick="generateEffects('${styleName}')">
                        <i class="fas fa-plus"></i> 生成特效
                    </button>
                </div>
            `;
            console.log('loadEffects: No effects found, hiding loading modal');
            hideLoading();
            return;
        }
        
        effects.forEach(effect => {
            const col = document.createElement('div');
            col.className = 'col-lg-4 col-md-6 col-sm-12 mb-4';
            
            const previewContent = effect.has_preview ? 
                `<video class="effect-preview" preload="metadata" muted>
                    <source src="/${effect.preview_file}" type="video/mp4">
                </video>` :
                `<div class="effect-preview-placeholder">
                    <i class="fas fa-video-slash"></i>
                </div>`;
            
            col.innerHTML = `
                <div class="card effect-card" onclick="showEffectDetails('${styleName}', '${effect.id}')">
                    <div class="position-relative">
                        ${previewContent}
                        <span class="badge bg-secondary badge-style">${getStyleDisplayName(styleName)}</span>
                    </div>
                    <div class="effect-info">
                        <div class="effect-title">${effect.name || effect.id}</div>
                        <div class="effect-description">${effect.description || '无描述'}</div>
                        <div class="effect-actions">
                            <button class="btn btn-sm btn-outline-primary" onclick="event.stopPropagation(); showEffectDetails('${styleName}', '${effect.id}')">
                                <i class="fas fa-eye"></i> 详情
                            </button>
                            ${effect.has_preview ? '' : 
                                `<button class="btn btn-sm btn-outline-success" onclick="event.stopPropagation(); generateSinglePreview('${styleName}', '${effect.id}')">
                                    <i class="fas fa-video"></i> 预览
                                </button>`}
                        </div>
                    </div>
                </div>
            `;
            
            effectsGrid.appendChild(col);
        });
        
        // 为视频添加播放事件
        document.querySelectorAll('.effect-preview').forEach(video => {
            video.addEventListener('mouseenter', () => {
                video.currentTime = 0;
                video.play().catch(() => {});
            });
            
            video.addEventListener('mouseleave', () => {
                video.pause();
                video.currentTime = 0;
            });
        });
        
    } catch (error) {
        console.error('Failed to load effects:', error);
        showAlert('加载特效列表失败', 'danger');
    } finally {
        console.log('loadEffects: Finally block - hiding loading modal');
        hideLoading();
    }
}

// 显示特效详情
async function showEffectDetails(styleName, effectId) {
    try {
        showLoading('正在加载特效详情...');
        
        const response = await fetch(`/api/effect/${styleName}/${effectId}`);
        const effect = await response.json();
        
        if (response.ok) {
            currentEffect = { styleName, effectId, ...effect };
            
            // 更新模态框内容
            document.getElementById('effectName').textContent = effect.name || effectId;
            document.getElementById('effectDescription').textContent = effect.description || '无描述';
            document.getElementById('effectAuthor').textContent = effect.author || '未知';
            document.getElementById('effectXml').textContent = effect.xml_content || '';
            
            // 设置预览视频
            const previewVideo = document.getElementById('previewVideo');
            const previewFile = `previews/${styleName}/${effectId}_preview.mp4`;
            
            // 检查预览文件是否存在
            fetch(`/${previewFile}`, { method: 'HEAD' })
                .then(response => {
                    if (response.ok) {
                        previewVideo.src = `/${previewFile}`;
                        previewVideo.style.display = 'block';
                    } else {
                        previewVideo.style.display = 'none';
                        document.getElementById('previewContainer').innerHTML = `
                            <div class="text-center p-4 bg-light">
                                <i class="fas fa-video-slash fa-3x text-muted mb-3"></i>
                                <p class="text-muted">暂无预览视频</p>
                                <button class="btn btn-success" onclick="generateSinglePreview()">
                                    <i class="fas fa-video"></i> 生成预览
                                </button>
                            </div>
                        `;
                    }
                });
            
            effectModal.show();
        } else {
            showAlert('加载特效详情失败', 'danger');
        }
    } catch (error) {
        console.error('Failed to load effect details:', error);
        showAlert('加载特效详情失败', 'danger');
    } finally {
        hideLoading();
    }
}

// 生成特效表单提交
async function handleGenerateSubmit(event) {
    event.preventDefault();
    
    const style = document.getElementById('generateStyle').value;
    const count = parseInt(document.getElementById('generateCount').value);
    
    if (!style) {
        showAlert('请选择风格', 'warning');
        return;
    }
    
    await generateEffects(style, count);
}

// 生成特效
async function generateEffects(style, count = 5) {
    try {
        showLoading('正在生成特效...');
        
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ style, count })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showAlert(`成功生成 ${result.generated_count} 个特效`, 'success');
            
            // 刷新数据
            await loadStyles();
            if (currentStyle === style) {
                await loadEffects(style);
            }
        } else {
            showAlert(`生成特效失败: ${result.error}`, 'danger');
        }
        
    } catch (error) {
        console.error('Failed to generate effects:', error);
        showAlert('生成特效失败', 'danger');
    } finally {
        hideLoading();
    }
}

// 生成单个预览
async function generateSinglePreview(styleName, effectId) {
    if (!styleName && currentEffect) {
        styleName = currentEffect.styleName;
        effectId = currentEffect.effectId;
    }
    
    if (!styleName || !effectId) {
        showAlert('参数错误', 'danger');
        return;
    }
    
    try {
        showLoading('正在生成预览视频...');
        
        const response = await fetch('/api/generate_preview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                style: styleName, 
                effect_id: effectId 
            })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            let message = '预览视频生成成功';
            if (result.demo_file) {
                message += `\nDemo已保存到: ${result.demo_file}`;
            }
            showAlert(message, 'success');
            
            // 更新预览视频
            if (currentEffect && currentEffect.styleName === styleName && currentEffect.effectId === effectId) {
                const previewVideo = document.getElementById('previewVideo');
                previewVideo.src = `/${result.preview_file}`;
                previewVideo.style.display = 'block';
                document.getElementById('previewContainer').innerHTML = `
                    <video id="previewVideo" class="w-100" controls style="max-height: 400px;">
                        <source src="/${result.preview_file}" type="video/mp4">
                    </video>
                `;
            }
            
            // 刷新特效列表
            if (currentStyle === styleName) {
                await loadEffects(styleName);
            }
            
        } else {
            showAlert(`生成预览失败: ${result.error}`, 'danger');
        }
        
    } catch (error) {
        console.error('Failed to generate preview:', error);
        showAlert('生成预览失败', 'danger');
    } finally {
        hideLoading();
    }
}

// 批量生成预览
async function generatePreviews() {
    if (!currentStyle) {
        showAlert('请先选择一个风格', 'warning');
        return;
    }
    
    if (confirm(`确定要为 ${getStyleDisplayName(currentStyle)} 风格的所有特效生成预览吗？`)) {
        try {
            showLoading('正在批量生成预览...');
            
            const response = await fetch('/api/generate_batch_preview', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ style: currentStyle })
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                showAlert(`批量预览完成！为 ${result.generated_count}/${result.total_effects} 个特效生成了预览\nDemo视频已保存到: ${result.demos_saved_to}`, 'success');
                
                // 刷新当前风格的特效列表
                await loadEffects(currentStyle);
            } else {
                showAlert(`批量预览失败: ${result.error}`, 'danger');
            }
            
        } catch (error) {
            console.error('Failed to generate batch previews:', error);
            showAlert('批量生成预览失败', 'danger');
        } finally {
            hideLoading();
        }
    }
}

// 下载特效
function downloadEffect() {
    if (!currentEffect) {
        showAlert('没有选中的特效', 'warning');
        return;
    }
    
    const url = `/effect/${currentEffect.styleName}/${currentEffect.effectId}.xml`;
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentEffect.effectId}.xml`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// 复制XML代码
function copyXml() {
    const xmlContent = document.getElementById('effectXml').textContent;
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(xmlContent).then(() => {
            showAlert('XML代码已复制到剪贴板', 'success');
        }).catch(() => {
            fallbackCopyTextToClipboard(xmlContent);
        });
    } else {
        fallbackCopyTextToClipboard(xmlContent);
    }
}

// 刷新数据
async function refreshData() {
    await loadStyles();
    if (currentStyle) {
        await loadEffects(currentStyle);
    }
    showAlert('数据已刷新', 'success');
}

// Demos相关功能
// 显示Demos模态框
async function showDemosModal() {
    try {
        if (!demosModal) {
            demosModal = new bootstrap.Modal(document.getElementById('demosModal'));
        }
        
        showLoading('正在加载Demo视频...');
        await loadDemos();
        demosModal.show();
        
    } catch (error) {
        console.error('Failed to show demos modal:', error);
        showAlert('加载Demo视频失败', 'danger');
    } finally {
        hideLoading();
    }
}

// 加载Demos列表
async function loadDemos() {
    try {
        const response = await fetch('/api/demos');
        allDemos = await response.json();
        
        displayDemos(allDemos);
        
    } catch (error) {
        console.error('Failed to load demos:', error);
        showAlert('加载Demo视频失败', 'danger');
    }
}

// 显示Demos列表
function displayDemos(demos) {
    const demosGrid = document.getElementById('demosGrid');
    const demosEmpty = document.getElementById('demosEmpty');
    
    if (demos.length === 0) {
        demosGrid.innerHTML = '';
        demosEmpty.style.display = 'block';
        return;
    }
    
    demosEmpty.style.display = 'none';
    demosGrid.innerHTML = '';
    
    demos.forEach(demo => {
        const col = document.createElement('div');
        col.className = 'col-lg-4 col-md-6 col-sm-12 mb-4';
        
        const fileSize = (demo.size / (1024 * 1024)).toFixed(2);
        const createdDate = new Date(demo.created * 1000).toLocaleString();
        
        col.innerHTML = `
            <div class="card demo-card">
                <div class="position-relative">
                    <video class="demo-preview w-100" preload="metadata" style="height: 200px; object-fit: cover;">
                        <source src="/${demo.path}" type="video/mp4">
                    </video>
                    <span class="badge bg-primary badge-style">${getStyleDisplayName(demo.style)}</span>
                </div>
                <div class="card-body">
                    <h6 class="card-title">${demo.effect_id}</h6>
                    <p class="card-text text-muted small">
                        <i class="fas fa-clock"></i> ${createdDate}<br>
                        <i class="fas fa-hdd"></i> ${fileSize} MB
                    </p>
                    <div class="d-flex gap-2">
                        <button class="btn btn-sm btn-primary" onclick="playDemoVideo('${demo.path}')">
                            <i class="fas fa-play"></i> 播放
                        </button>
                        <button class="btn btn-sm btn-success" onclick="downloadDemo('${demo.path}', '${demo.filename}')">
                            <i class="fas fa-download"></i> 下载
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteDemo('${demo.path}', '${demo.filename}')">
                            <i class="fas fa-trash"></i> 删除
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        demosGrid.appendChild(col);
    });
    
    // 为视频添加播放事件
    document.querySelectorAll('.demo-preview').forEach(video => {
        video.addEventListener('mouseenter', () => {
            video.currentTime = 0;
            video.play().catch(() => {});
        });
        
        video.addEventListener('mouseleave', () => {
            video.pause();
            video.currentTime = 0;
        });
    });
}

// 过滤Demos
function filterDemos() {
    const searchTerm = document.getElementById('demoSearch').value.toLowerCase();
    const filteredDemos = allDemos.filter(demo => 
        demo.filename.toLowerCase().includes(searchTerm) ||
        demo.style.toLowerCase().includes(searchTerm) ||
        demo.effect_id.toLowerCase().includes(searchTerm)
    );
    displayDemos(filteredDemos);
}

// 刷新Demos
async function refreshDemos() {
    await loadDemos();
    showAlert('Demo列表已刷新', 'success');
}

// 播放Demo视频
function playDemoVideo(demoPath) {
    // 在新窗口中打开视频
    window.open(`/${demoPath}`, '_blank');
}

// 下载Demo
function downloadDemo(demoPath, filename) {
    const a = document.createElement('a');
    a.href = `/${demoPath}`;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// 删除Demo
async function deleteDemo(demoPath, filename) {
    if (confirm(`确定要删除 ${filename} 吗？`)) {
        try {
            // 这里需要后端支持删除API
            showAlert('删除功能开发中...', 'info');
        } catch (error) {
            showAlert('删除失败', 'danger');
        }
    }
}

// 打包下载所有Demos
function downloadAllDemos() {
    // 这里需要后端支持打包下载API
    showAlert('打包下载功能开发中...', 'info');
}

// 工具函数
function getStyleIcon(styleName) {
    const icons = {
        shake: 'fas fa-wave-square',
        zoom: 'fas fa-search-plus',
        blur: 'fas fa-eye-slash',
        transition: 'fas fa-exchange-alt',
        glitch: 'fas fa-bolt',
        color: 'fas fa-palette'
    };
    return icons[styleName] || 'fas fa-magic';
}

function getStyleDisplayName(styleName) {
    const names = {
        shake: '抖动',
        zoom: '缩放',
        blur: '模糊',
        transition: '转场',
        glitch: '故障',
        color: '色彩'
    };
    return names[styleName] || styleName;
}

function showAlert(message, type = 'info') {
    // 创建alert元素
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // 3秒后自动移除
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 3000);
}

function showLoading(message = '加载中...') {
    console.log('showLoading called with message:', message);
    
    // Use the simple overlay instead of Bootstrap modal
    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingMessage = document.getElementById('loadingMessage');
    
    if (loadingOverlay && loadingMessage) {
        loadingMessage.textContent = message;
        loadingOverlay.style.display = 'flex';
        console.log('Loading overlay shown');
    } else {
        console.error('Loading overlay elements not found');
    }
}

function hideLoading() {
    console.log('hideLoading called');
    
    // Use the simple overlay instead of Bootstrap modal
    const loadingOverlay = document.getElementById('loadingOverlay');
    
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
        console.log('Loading overlay hidden');
    } else {
        console.error('Loading overlay element not found');
    }
}

function showProgressModal(message) {
    document.getElementById('progressMessage').textContent = message;
    progressModal.show();
}

function hideProgressModal() {
    progressModal.hide();
}

function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.top = '0';
    textArea.style.left = '0';
    textArea.style.position = 'fixed';
    
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showAlert('XML代码已复制到剪贴板', 'success');
        } else {
            showAlert('复制失败，请手动复制', 'warning');
        }
    } catch (err) {
        showAlert('复制失败，请手动复制', 'warning');
    }
    
    document.body.removeChild(textArea);
}
