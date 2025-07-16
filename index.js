const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const path = require('path');
const crypto = require('crypto');
const axios = require('axios');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// 存储房间和用户信息
const rooms = new Map();
const users = new Map();

// 管理员IP列表 - 请根据实际情况配置
const adminIPs = [
    '127.0.0.1',
    '::1',
    'localhost',
    '192.168.1.100',
    '10.0.0.1',
    '54.169.98.46',
    '35.221.223.198',  // 根据控制台输出添加的IP
    '10.84.1.45',      // 内网IP
    '10.84.2.110',     // 内网IP
    '10.84.0.41',      // 内网IP
    '10.84.6.150'      // 内网IP
    // 注意：请在这里添加您的真实IP地址以获得管理员权限
];

// 静态文件服务
app.use(express.static('.'));

// 获取客户端真实IP地址
function getClientIP(req) {
    // 尝试从多个头部获取真实IP
    const forwarded = req.headers['x-forwarded-for'];
    const real = req.headers['x-real-ip'];
    const remoteAddress = req.connection.remoteAddress || req.socket.remoteAddress;

    if (forwarded) {
        // x-forwarded-for 可能包含多个IP，取第一个
        return forwarded.split(',')[0].trim();
    }

    if (real) {
        return real;
    }

    // 处理IPv6映射的IPv4地址
    if (remoteAddress) {
        if (remoteAddress.startsWith('::ffff:')) {
            return remoteAddress.substring(7); // 移除 ::ffff: 前缀
        }
        return remoteAddress;
    }

    return '127.0.0.1';
}

// 生成用户名
function generateUsername() {
    const adjectives = ['神秘', '匿名', '隐形', '未知', '幽灵', '影子', '秘密', '无名'];
    const nouns = ['访客', '用户', '旅客', '探索者', '观察者', '路人', '游客', '新人'];
    const adj = adjectives[Math.floor(Math.random() * adjectives.length)];
    const noun = nouns[Math.floor(Math.random() * nouns.length)];
    const num = Math.floor(Math.random() * 1000);
    return `${adj}${noun}${num}`;
}

// 服务器端检测用户IP是否为Tor节点
async function detectTorIP(ip) {
    try {
        const results = {
            isTor: false,
            torExitNode: false,
            ipInfo: null,
            detectionDetails: [],
            error: null
        };

        console.log(`开始检测IP ${ip} 是否为Tor节点...`);

        // 方法1: 检查Tor出口节点列表
        try {
            const exitListResponse = await axios.get('https://check.torproject.org/torbulkexitlist', {
                timeout: 5000,
                headers: {
                    'User-Agent': 'Anonymous-Chatroom-Server/1.0'
                }
            });

            if (exitListResponse.data && exitListResponse.data.includes(ip)) {
                results.isTor = true;
                results.torExitNode = true;
                results.detectionDetails.push('✓ Tor出口节点列表: 确认为Tor出口节点');
                console.log(`IP ${ip} 在Tor出口节点列表中`);
            } else {
                results.detectionDetails.push('✗ Tor出口节点列表: 非出口节点');
            }
        } catch (error) {
            console.warn('Tor出口节点列表检测失败:', error.message);
            results.detectionDetails.push('⚠ Tor出口节点列表: 检测失败 (网络错误)');
        }

        // 方法2: 使用Tor Project官方API
        try {
            const torApiUrl = `https://check.torproject.org/api/ip?ip=${encodeURIComponent(ip)}`;
            const torResponse = await axios.get(torApiUrl, {
                timeout: 5000,
                headers: {
                    'User-Agent': 'Anonymous-Chatroom-Server/1.0'
                }
            });

            if (torResponse.data && torResponse.data.IsTor === true) {
                results.isTor = true;
                results.detectionDetails.push('✓ Tor官方API: 确认为Tor节点');
                console.log(`IP ${ip} 被Tor官方API确认为Tor节点`);
            } else {
                results.detectionDetails.push('✗ Tor官方API: 非Tor节点');
            }
        } catch (error) {
            console.warn('Tor官方API检测失败:', error.message);
            results.detectionDetails.push('⚠ Tor官方API: 检测失败 (可能被限制访问)');
        }

        // 方法3: 获取IP详细信息并进行启发式检测
        try {
            const ipinfoUrl = `https://ipinfo.io/${encodeURIComponent(ip)}/json`;
            const ipinfoResponse = await axios.get(ipinfoUrl, {
                timeout: 5000,
                headers: {
                    'User-Agent': 'Anonymous-Chatroom-Server/1.0'
                }
            });

            if (ipinfoResponse.data) {
                results.ipInfo = ipinfoResponse.data;

                // 启发式检测: 检查ISP/组织信息中的Tor关键词
                const org = (ipinfoResponse.data.org || '').toLowerCase();
                const hostname = (ipinfoResponse.data.hostname || '').toLowerCase();
                const torKeywords = ['tor', 'onion', 'relay', 'exit', 'proxy', 'anonymous', 'privacy', 'vpn'];

                const hasTorKeywords = torKeywords.some(keyword => 
                    org.includes(keyword) || hostname.includes(keyword)
                );

                if (hasTorKeywords && !results.isTor) {
                    results.isTor = true;
                    results.detectionDetails.push(`✓ 启发式检测: 疑似Tor节点 (ISP: ${ipinfoResponse.data.org})`);
                    console.log(`IP ${ip} 通过启发式检测判断为可能的Tor节点`);
                } else {
                    results.detectionDetails.push(`✗ 启发式检测: 普通节点 (ISP: ${ipinfoResponse.data.org || '未知'})`);
                }
            }
        } catch (error) {
            console.warn('IPInfo检测失败:', error.message);
            results.detectionDetails.push('⚠ IPInfo检测: 获取IP信息失败');
        }

        // 方法4: 使用备用IP信息服务
        if (!results.ipInfo) {
            try {
                const backupServices = [
                    'https://httpbin.org/ip',
                    'https://api.ip.sb/geoip/' + encodeURIComponent(ip),
                    'https://ip-api.com/json/' + encodeURIComponent(ip)
                ];

                for (const service of backupServices) {
                    try {
                        const response = await axios.get(service, {
                            timeout: 3000,
                            headers: {
                                'User-Agent': 'Anonymous-Chatroom-Server/1.0'
                            }
                        });

                        if (response.data) {
                            results.ipInfo = response.data;
                            results.detectionDetails.push('✓ 备用服务: 获取到IP信息');
                            break;
                        }
                    } catch (e) {
                        continue;
                    }
                }
            } catch (error) {
                console.warn('备用IP服务检测失败:', error.message);
            }
        }

        console.log(`IP ${ip} Tor检测完成:`, results.isTor ? '是Tor节点' : '非Tor节点');
        return results;

    } catch (error) {
        console.error('Tor检测过程中发生错误:', error);
        return {
            isTor: false,
            torExitNode: false,
            ipInfo: null,
            detectionDetails: ['❌ 检测过程发生错误: ' + error.message],
            error: error.message
        };
    }
}

// 服务器端获取详细的IP地理信息
async function getDetailedIPInfo(ip) {
    try {
        const services = [
            {
                url: `https://ipinfo.io/${encodeURIComponent(ip)}/json`,
                name: 'IPInfo.io'
            },
            {
                url: `https://ip-api.com/json/${encodeURIComponent(ip)}?fields=status,message,continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,offset,currency,isp,org,as,asname,reverse,mobile,proxy,hosting,query`,
                name: 'IP-API.com'
            },
            {
                url: `https://api.ip.sb/geoip/${encodeURIComponent(ip)}`,
                name: 'IP.SB'
            }
        ];

        for (const service of services) {
            try {
                console.log(`尝试从 ${service.name} 获取IP ${ip} 的详细信息...`);
                const response = await axios.get(service.url, {
                    timeout: 5000,
                    headers: {
                        'User-Agent': 'Anonymous-Chatroom-Server/1.0'
                    }
                });

                if (response.data && (response.data.status !== 'fail')) {
                    console.log(`成功从 ${service.name} 获取到IP信息`);
                    return {
                        success: true,
                        data: response.data,
                        source: service.name
                    };
                }
            } catch (error) {
                console.warn(`${service.name} 服务失败:`, error.message);
                continue;
            }
        }

        return {
            success: false,
            error: '所有IP信息服务都无法访问',
            source: null
        };

    } catch (error) {
        console.error('获取详细IP信息时发生错误:', error);
        return {
            success: false,
            error: error.message,
            source: null
        };
    }
}

// 检查是否为管理员IP
function isAdminIP(ip) {
    // 直接匹配
    if (adminIPs.includes(ip)) {
        return true;
    }

    // 检查是否为IPv6映射的IPv4地址
    if (ip.startsWith('::ffff:')) {
        const ipv4 = ip.substring(7);
        if (adminIPs.includes(ipv4)) {
            return true;
        }
    }

    // 检查localhost变体
    const localhostVariants = ['127.0.0.1', '::1', 'localhost'];
    if (localhostVariants.includes(ip)) {
        return adminIPs.some(adminIP => localhostVariants.includes(adminIP));
    }

    return false;
}

// 创建用户对象
function createUser(ws, req) {
    const ip = getClientIP(req);
    const isAdmin = isAdminIP(ip);
    const user = {
        id: crypto.randomUUID(),
        username: generateUsername(),
        ip: ip,
        isAdmin: isAdmin,
        joinTime: new Date(),
        lastActivity: new Date(),
        isOnline: true,
        userAgent: req.headers['user-agent'] || 'Unknown',
        roomId: null,
        ws: ws,
        torDetection: null,
        ipInfo: null,
        detectionInProgress: false
    };

    users.set(user.id, user);
    ws.userId = user.id;

    // 输出调试信息
    console.log(`用户创建 - IP: ${ip}, 管理员: ${isAdmin}, 配置的管理员IP: [${adminIPs.join(', ')}]`);

    // 异步进行服务器端检测
    performServerSideDetection(user);

    return user;
}

// 执行服务器端检测
async function performServerSideDetection(user) {
    if (user.detectionInProgress) return;

    user.detectionInProgress = true;
    console.log(`开始对用户 ${user.username} (${user.ip}) 进行服务器端检测...`);

    try {
        // 并行执行Tor检测和IP信息获取
        const [torResult, ipInfoResult] = await Promise.all([
            detectTorIP(user.ip),
            getDetailedIPInfo(user.ip)
        ]);

        user.torDetection = torResult;
        user.ipInfo = ipInfoResult;
        user.detectionInProgress = false;

        console.log(`用户 ${user.username} 检测完成 - Tor: ${torResult.isTor ? '是' : '否'}, IP信息: ${ipInfoResult.success ? '成功' : '失败'}`);

        // 通知管理员用户检测完成
        broadcastDetectionResults(user);

    } catch (error) {
        console.error(`用户 ${user.username} 检测失败:`, error);
        user.detectionInProgress = false;
        user.torDetection = {
            isTor: false,
            detectionDetails: ['❌ 服务器端检测失败: ' + error.message],
            error: error.message
        };
        user.ipInfo = {
            success: false,
            error: error.message
        };
    }
}

// 向管理员广播检测结果
function broadcastDetectionResults(user) {
    // 向所有管理员发送检测结果更新
    users.forEach(admin => {
        if (admin.isAdmin && admin.ws && admin.ws.readyState === WebSocket.OPEN) {
            admin.ws.send(JSON.stringify({
                type: 'userDetectionUpdate',
                targetUserId: user.id,
                torDetection: user.torDetection,
                ipInfo: user.ipInfo
            }));
        }
    });
}

// 获取房间用户列表
function getRoomUsers(roomId) {
    const room = rooms.get(roomId);
    if (!room) return [];

    return Array.from(room.users.values()).map(user => ({
        id: user.id,
        username: user.username,
        isAdmin: user.isAdmin,
        joinTime: user.joinTime,
        isOnline: user.isOnline,
        ip: user.isAdmin ? undefined : user.ip // 普通用户看不到管理员IP，管理员看不到自己IP在列表中
    }));
}

// 广播消息到房间
function broadcastToRoom(roomId, message, excludeUserId = null) {
    const room = rooms.get(roomId);
    if (!room) return;

    room.users.forEach(user => {
        if (user.id !== excludeUserId && user.ws.readyState === WebSocket.OPEN) {
            user.ws.send(JSON.stringify(message));
        }
    });
}

// 发送系统消息到房间
function sendSystemMessage(roomId, message, excludeUserId = null) {
    broadcastToRoom(roomId, {
        type: 'systemMessage',
        message: message,
        timestamp: new Date()
    }, excludeUserId);
}

// WebSocket连接处理
wss.on('connection', (ws, req) => {
    const user = createUser(ws, req);

    console.log(`用户 ${user.username} (${user.ip}) 已连接 - 管理员: ${user.isAdmin}`);

    // 发送用户初始化信息
    ws.send(JSON.stringify({
        type: 'userInit',
        user: {
            id: user.id,
            username: user.username,
            ip: user.ip,
            isAdmin: user.isAdmin,
            joinTime: user.joinTime
        }
    }));

    // 处理消息
    ws.on('message', (data) => {
        try {
            const message = JSON.parse(data);
            const currentUser = users.get(ws.userId);

            if (!currentUser) return;

            currentUser.lastActivity = new Date();

            switch (message.type) {
                case 'joinRoom':
                    handleJoinRoom(currentUser, message.roomId || 'default-room');
                    break;

                case 'sendMessage':
                    handleSendMessage(currentUser, message.text);
                    break;

                case 'getUserDetails':
                    handleGetUserDetails(currentUser, message.targetUserId);
                    break;

                case 'kickUser':
                    handleKickUser(currentUser, message.targetUserId);
                    break;

                case 'heartbeat':
                    ws.send(JSON.stringify({ type: 'pong' }));
                    break;

                case 'requestDetection':
                    handleRequestDetection(currentUser, message.targetUserId);
                    break;
            }
        } catch (error) {
            console.error('消息处理错误:', error);
        }
    });

    // 连接关闭处理
    ws.on('close', () => {
        handleUserDisconnect(user);
    });

    // 错误处理
    ws.on('error', (error) => {
        console.error('WebSocket错误:', error);
    });
});

// 处理加入房间
function handleJoinRoom(user, roomId) {
    // 离开当前房间
    if (user.roomId) {
        leaveRoom(user, user.roomId);
    }

    // 创建房间如果不存在
    if (!rooms.has(roomId)) {
        rooms.set(roomId, {
            id: roomId,
            users: new Map(),
            messages: []
        });
    }

    const room = rooms.get(roomId);
    room.users.set(user.id, user);
    user.roomId = roomId;

    // 发送加入成功消息
    user.ws.send(JSON.stringify({
        type: 'joinedRoom',
        success: true,
        roomId: roomId
    }));

    // 发送当前用户列表
    const roomUsers = getRoomUsers(roomId);
    user.ws.send(JSON.stringify({
        type: 'userList',
        users: roomUsers,
        onlineCount: roomUsers.length
    }));

    // 通知其他用户有新用户加入
    broadcastToRoom(roomId, {
        type: 'userJoined',
        user: {
            id: user.id,
            username: user.username,
            isAdmin: user.isAdmin,
            joinTime: user.joinTime,
            isOnline: true
        }
    }, user.id);

    // 发送系统消息
    sendSystemMessage(roomId, `${user.username} 加入了聊天室`, user.id);

    console.log(`用户 ${user.username} 加入房间 ${roomId}`);
}

// 处理离开房间
function leaveRoom(user, roomId) {
    const room = rooms.get(roomId);
    if (!room) return;

    room.users.delete(user.id);

    // 通知其他用户
    broadcastToRoom(roomId, {
        type: 'userLeft',
        user: {
            id: user.id,
            username: user.username,
            isAdmin: user.isAdmin
        }
    });

    // 发送系统消息
    sendSystemMessage(roomId, `${user.username} 离开了聊天室`);

    // 如果房间为空，删除房间
    if (room.users.size === 0) {
        rooms.delete(roomId);
    }
}

// 处理发送消息
function handleSendMessage(user, text) {
    if (!user.roomId || !text || text.trim().length === 0) {
        return;
    }

    const message = {
        id: crypto.randomUUID(),
        text: text.trim(),
        sender: {
            id: user.id,
            username: user.username,
            isAdmin: user.isAdmin
        },
        timestamp: new Date(),
        roomId: user.roomId
    };

    // 保存消息到房间
    const room = rooms.get(user.roomId);
    if (room) {
        room.messages.push(message);

        // 限制消息历史记录数量
        if (room.messages.length > 1000) {
            room.messages = room.messages.slice(-500);
        }
    }

    // 广播消息到房间所有用户
    broadcastToRoom(user.roomId, {
        type: 'newMessage',
        message: message
    });

    console.log(`${user.username} 在房间 ${user.roomId} 发送消息: ${text}`);
}

// 处理获取用户详情（仅管理员）
function handleGetUserDetails(requester, targetUserId) {
    if (!requester.isAdmin) {
        requester.ws.send(JSON.stringify({
            type: 'error',
            message: '权限不足'
        }));
        return;
    }

    const targetUser = users.get(targetUserId);
    if (!targetUser) {
        requester.ws.send(JSON.stringify({
            type: 'error',
            message: '用户不存在'
        }));
        return;
    }

    // 发送详细用户信息，包含服务器端检测结果
    requester.ws.send(JSON.stringify({
        type: 'userDetails',
        user: {
            id: targetUser.id,
            username: targetUser.username,
            ip: targetUser.ip,
            isAdmin: targetUser.isAdmin,
            joinTime: targetUser.joinTime,
            lastActivity: targetUser.lastActivity,
            isOnline: targetUser.isOnline,
            userAgent: targetUser.userAgent,
            roomId: targetUser.roomId,
            torDetection: targetUser.torDetection,
            ipInfo: targetUser.ipInfo,
            detectionInProgress: targetUser.detectionInProgress
        }
    }));
}

// 处理踢出用户（仅管理员）
function handleKickUser(requester, targetUserId) {
    if (!requester.isAdmin) {
        requester.ws.send(JSON.stringify({
            type: 'error',
            message: '权限不足'
        }));
        return;
    }

    const targetUser = users.get(targetUserId);
    if (!targetUser) {
        requester.ws.send(JSON.stringify({
            type: 'error',
            message: '用户不存在'
        }));
        return;
    }

    if (targetUser.isAdmin) {
        requester.ws.send(JSON.stringify({
            type: 'error',
            message: '无法踢出管理员'
        }));
        return;
    }

    // 发送踢出消息给目标用户
    if (targetUser.ws.readyState === WebSocket.OPEN) {
        targetUser.ws.send(JSON.stringify({
            type: 'kicked',
            message: '您已被管理员踢出聊天室'
        }));

        setTimeout(() => {
            targetUser.ws.close();
        }, 1000);
    }

    console.log(`管理员 ${requester.username} 踢出了用户 ${targetUser.username}`);
}

// 处理请求检测
function handleRequestDetection(requester, targetUserId) {
    if (!requester.isAdmin) {
        requester.ws.send(JSON.stringify({
            type: 'error',
            message: '权限不足'
        }));
        return;
    }

    const targetUser = users.get(targetUserId);
    if (!targetUser) {
        requester.ws.send(JSON.stringify({
            type: 'error',
            message: '用户不存在'
        }));
        return;
    }

    // 如果检测正在进行或已完成，直接返回结果
    if (targetUser.torDetection && targetUser.ipInfo) {
        requester.ws.send(JSON.stringify({
            type: 'userDetectionUpdate',
            targetUserId: targetUser.id,
            torDetection: targetUser.torDetection,
            ipInfo: targetUser.ipInfo
        }));
    } else if (!targetUser.detectionInProgress) {
        // 重新开始检测
        performServerSideDetection(targetUser);
        requester.ws.send(JSON.stringify({
            type: 'userDetectionUpdate',
            targetUserId: targetUser.id,
            detectionInProgress: true
        }));
    } else {
        // 检测正在进行中
        requester.ws.send(JSON.stringify({
            type: 'userDetectionUpdate',
            targetUserId: targetUser.id,
            detectionInProgress: true
        }));
    }
}

// 处理用户断开连接
function handleUserDisconnect(user) {
    if (user.roomId) {
        leaveRoom(user, user.roomId);
    }

    users.delete(user.id);
    console.log(`用户 ${user.username} (${user.ip}) 已断开连接`);
}

// 心跳检测
setInterval(() => {
    wss.clients.forEach(ws => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
        }
    });
}, 30000);

// 清理离线用户
setInterval(() => {
    const now = new Date();
    users.forEach(user => {
        if (now - user.lastActivity > 60000) { // 1分钟无活动
            if (user.ws.readyState !== WebSocket.OPEN) {
                handleUserDisconnect(user);
            }
        }
    });
}, 60000);

// 启动服务器
const PORT = process.env.PORT || 5000;
server.listen(PORT, '0.0.0.0', () => {
    console.log(`聊天服务器运行在端口 ${PORT}`);
    console.log(`WebSocket地址: ws://localhost:${PORT}`);
});

// 优雅关闭
process.on('SIGTERM', () => {
    console.log('正在关闭服务器...');
    server.close(() => {
        console.log('服务器已关闭');
        process.exit(0);
    });
});