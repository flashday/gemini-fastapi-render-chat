document.addEventListener('DOMContentLoaded', () => {
    // 获取 DOM 元素
    const chatLog = document.getElementById('chat-log');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const loadingIndicator = document.getElementById('loading');
 
    // 客户端维护的对话历史，这是实现无状态后端的关键
    let chatHistory = [];
 
    // 渲染聊天记录到界面
    function renderChatLog() {
        chatLog.innerHTML = ''; // 清空现有内容
        chatHistory.forEach(message => {
            const messageElement = document.createElement('div');
            messageElement.classList.add('message');
            
            // 根据角色添加不同的 CSS 类
            if (message.role === 'user') {
                messageElement.classList.add('user-message');
            } else if (message.role === 'model') {
                messageElement.classList.add('bot-message');
            } else {
                messageElement.classList.add('error-message');
            }
            
            messageElement.textContent = message.content;
            chatLog.appendChild(messageElement);
        });
        // 自动滚动到最新消息
        chatLog.scrollTop = chatLog.scrollHeight;
    }
 
    // 处理表单提交
    async function handleFormSubmit(event) {
        event.preventDefault(); // 阻止表单默认的页面刷新行为
        
        const userMessage = userInput.value.trim();
        if (!userMessage) return;
 
        // 1. 将用户消息添加到历史记录并更新 UI
        chatHistory.push({ role: 'user', content: userMessage });
        renderChatLog();
        userInput.value = ''; // 清空输入框
        loadingIndicator.classList.remove('hidden'); // 显示加载动画
 
        try {
            // 2. 构建发送到后端的请求体
            // 注意：我们发送的是当前消息和之前的历史
            const requestBody = {
                message: userMessage,
                history: chatHistory.slice(0, -1) // 发送除当前用户消息外的所有历史
            };
 
            // 3. 使用 Fetch API 调用后端
            const response = await fetch('http://127.0.0.1:8000/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody),
            });
 
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'API 请求失败');
            }
 
            const data = await response.json();
 
            // 4. 将机器人回复添加到历史记录并更新 UI
            chatHistory.push({ role: 'model', content: data.reply });
 
        } catch (error) {
            console.error('Error:', error);
            // 将错误信息也显示在聊天记录中
            chatHistory.push({ role: 'error', content: `错误: ${error.message}` });
        } finally {
            // 5. 无论成功与否，都隐藏加载动画并重新渲染
            loadingIndicator.classList.add('hidden');
            renderChatLog();
        }
    }
 
    // 为表单添加提交事件监听器
    chatForm.addEventListener('submit', handleFormSubmit);
 
    // 初始欢迎语
    chatHistory.push({ role: 'model', content: '你好！我是 Gemini。有什么可以帮助你的吗？' });
    renderChatLog();
});
