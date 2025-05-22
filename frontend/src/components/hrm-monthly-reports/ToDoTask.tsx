import React, { useState } from "react";
import { Typography, Input, Button, List } from "antd";
import { PlusOutlined, DeleteOutlined } from "@ant-design/icons";

const { Title } = Typography;

const ToDoTask: React.FC = () => {
  const [tasks, setTasks] = useState<{ id: number; text: string }[]>([]);
  const [newTask, setNewTask] = useState("");
  const [taskCounter, setTaskCounter] = useState(1); // ✅ Dùng biến `taskCounter` để tạo ID tăng dần

  // Xử lý thêm Task với ID tăng dần
  const handleAddTask = () => {
    if (!newTask.trim()) return;
    setTasks([...tasks, { id: taskCounter, text: newTask }]);
    setTaskCounter((prev) => prev + 1); // ✅ Tăng ID lên 1 mỗi lần thêm task
    setNewTask("");
  };

  // Xóa Task
  const handleDeleteTask = (id: number) => {
    setTasks(tasks.filter((task) => task.id !== id));
  };

  return (
    <div style={{ width: "250px", padding: "10px", border: "1px solid #ddd", borderRadius: "5px", background: "#fff" }}>
      <Title level={5}>Danh sách công việc</Title>
      <Input
        placeholder="Nhập công việc cần làm"
        value={newTask}
              onChange={(e) => setNewTask(e.target.value)}
              onPressEnter={handleAddTask}
          />
          <Button icon={<PlusOutlined />} onClick={handleAddTask} style={{ marginTop: 5 }}>
              Thêm công việc
          </Button>
          <List
              bordered
              dataSource={tasks}
              renderItem={(task) => (
                  <List.Item key={task.id}> {/* ✅ Thêm key */}
                      {task.text}
                  </List.Item>
              )}
          />

      </div>
  );
};

export default ToDoTask;
