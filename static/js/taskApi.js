/**
 * 向后端API发送POST请求来添加新任务
 * @param {string} name - 任务名称
 * @param {string} description - 任务描述
 * @returns {Promise} - 返回包含新创建任务数据的Promise
 */
async function addTask(name, description) {
    try {
        const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                description: description
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.task;
    } catch (error) {
        console.error('添加任务时出错:', error);
        throw error;
    }
}

// 使用示例：
/*
addTask('完成报告', '准备季度报告文档')
    .then(task => {
        console.log('任务已创建:', task);
    })
    .catch(error => {
        console.error('创建任务失败:', error);
    });
*/