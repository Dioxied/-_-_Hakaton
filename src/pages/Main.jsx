
import React, { useState, useEffect } from 'react';
import '../style/Main.css';

function getUserIdFromToken(token) {
    if (!token) return null;
    try {
      const payload = token.split('.')[1];
      const decoded = JSON.parse(atob(payload));
      return decoded.user_id;
    } catch (e) {
      console.error('Ошибка декодирования токена:', e);
      return null;
    }
  }

const Main = () => {
  // Состояния для фильтра, списка чатов, выбранного чата, сообщений, ввода, файлов, звонка и создания чата
  const [selectedFilter, setSelectedFilter] = useState('');
  const [chats, setChats] = useState([]);
  const [currentChat, setCurrentChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMsg, setInputMsg] = useState('');
  const [callLink, setCallLink] = useState('');
  const [showCreateChat, setShowCreateChat] = useState(false);
  const [newChatTitle, setNewChatTitle] = useState('');
  const [newChatType, setNewChatType] = useState('text'); // варианты: 'text', 'voice', 'vcs'
  const [newChatStatus, setNewChatStatus] = useState('active');

  // Предполагается, что токен хранится в cookie (можно заменить на контекст авторизации)
  const token = document.cookie.split(';')[0].split('=')[1];

  // При изменении фильтра загружаем список чатов (например, для проекта с id=1)
  useEffect(() => {
    fetch(`http://192.168.0.105:8000/chats/1?type=${selectedFilter}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })
      .then(res => res.json())
      .then(data => setChats(data.chats))
      .catch(err => console.error(err));
  }, [selectedFilter, token]);

  // При выборе чата загружаем его сообщения
  const handleSelectChat = (chat) => {
    setCurrentChat(chat);
    fetch(`http://192.168.0.105:8000/messages/${chat.id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })
      .then(res => res.json())
      .then(data => setMessages(data.messages))
      .catch(err => console.error(err));
  };


  const sendMessage = () => {
    if (!inputMsg || !currentChat) return;
    const user_id = getUserIdFromToken(token);
    if (!user_id) return;
    const payload = {
      chat_id: currentChat.id,
      sender_id: user_id,
      content: inputMsg,
      markdown_enabled: false,
      voice_note_url: None,
      file_url: null,
      message_type: 'text'
    };


    fetch('http://192.168.0.105:8000/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    })
      .then(res => res.json())
      .then(() => {
        setInputMsg('');
        // Обновляем сообщения после отправки
        return fetch(`http://192.168.0.105:8000/messages/${currentChat.id}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        });
      })
      .then(res => res.json())
      .then(data => setMessages(data.messages))
      .catch(err => console.error(err));
  };

  // Загрузка файла
  const uploadFile = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('uploader_id', 1); // заменить на настоящий id пользователя

    fetch('http://192.168.0.105:8000/files/upload', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    })
      .then(res => res.json())
      .then(data => {
        console.log('File uploaded:', data);
        // При необходимости можно добавить сообщение с ссылкой на файл в чат
      })
      .catch(err => console.error(err));
  };

  // Создание сессии звонка
  const createCallSession = () => {
    if (!currentChat) return;
    const payload = {
      chat_id: currentChat.id,
      scheduled_start: new Date().toISOString(),
      scheduled_end: new Date(new Date().getTime() + 3600000).toISOString() // через 1 час
    };

    fetch('http://192.168.0.105:8000/calls', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    })
      .then(res => res.json())
      .then(data => setCallLink(data.call_link))
      .catch(err => console.error(err));
  };

  // Создание нового чата
  const createChat = () => {
    const payload = {
      project_id: 1, // для примера, проект с id = 1
      title: newChatTitle,
      chat_type: newChatType,
      status: newChatStatus
    };

    fetch('http://192.168.0.105:8000/chats', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    })
      .then(res => res.json())
      .then(data => {
        console.log('Chat created:', data);
        setShowCreateChat(false);
        setNewChatTitle('');
        // Обновляем список чатов
        return fetch(`http://192.168.0.105:8000/chats/1?type=${selectedFilter}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        });
      })
      .then(res => res.json())
      .then(data => setChats(data.chats))
      .catch(err => console.error(err));
  };

  return (
    <div className="bg2">
      <div className="leftcol">
        <div className="nav">
          Сортировать по
          <select onChange={(e) => setSelectedFilter(e.target.value)}>
            <option value="">Все</option>
            <option value="1">Инвестиции</option>
            <option value="2">Оборудование</option>
            <option value="3">Экспертиза</option>
            <option value="4">Статус</option>
            <option value="5">Участники</option>
          </select>
          
        </div>
        <div className="chats">
          {chats && chats.map(chat => (
            <div key={chat.id} onClick={() => handleSelectChat(chat)}>
              {chat.title}
            </div>
          ))}
        </div>
        
        {showCreateChat && (
          <div className="create-chat-modal">
            <h3>Создать новый чат</h3>
            <input className='create-chat-modal_margin'
              type="text"
              placeholder="Название чата"
              value={newChatTitle}
              onChange={(e) => setNewChatTitle(e.target.value)}
            />
            <select className='create-chat-modal_margin' value={newChatType} onChange={(e) => setNewChatType(e.target.value)}>
              <option value="text">Текстовый</option>
              <option value="voice">Голосовой</option>
              <option value="vcs">Видеоконференция</option>
            </select>
            <select className='create-chat-modal_margin' value={newChatStatus} onChange={(e) => setNewChatStatus(e.target.value)}>
              <option value="active">Активный</option>
              <option value="archived">Архивный</option>
            </select>
            <button className='create-chat-modal_margin' onClick={createChat}>Создать чат</button>
            <button className='create-chat-modal_margin' onClick={() => setShowCreateChat(false)}>Отмена</button>
          </div>
        )}
        
      </div>
      <button className="addchat" onClick={() => setShowCreateChat(true)}>+</button>
      <div className="chat">
        <div className="mininav">
          <button className="lilbtn" onClick={createCallSession}>Созвать</button>
          <button className="lilbtn" onClick={() => { /* логика открытия файлообменника, если нужно */ }}>
            Файлы
          </button>
        </div>
        <div className="msgfield">
          {messages && messages.map(msg => (
            <div key={msg.id}>
              <strong>{msg.sender_id}</strong>: {msg.content}
              {msg.file_url && (
                <a href={msg.file_url} target="_blank" rel="noopener noreferrer">
                  [Файл]
                </a>
              )}
            </div>
          ))}
        </div>
        <div className="inpfield">
          <input
            type="text"
            className="inpt"
            value={inputMsg}
            onChange={(e) => setInputMsg(e.target.value)}
            placeholder="Введите сообщение..."
          />
          <button className="lilbtn" onClick={sendMessage}>Отправить</button>
          <input className="fail" type="file" onChange={uploadFile} />
          {callLink && (
            <div className="callLink">
              <a href={callLink} target="_blank" rel="noopener noreferrer">
                Присоединиться к звонку
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Main;
