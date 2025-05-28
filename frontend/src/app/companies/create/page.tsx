"use client";
import React, { useState } from "react";
import { Button, Form, Input, Modal, Table, Space, Popconfirm, Card, Typography } from "antd";

interface SubCompany {
  id: number;
  name: string;
  code: string;
}

export default function CompanyCreate() {
  const [form] = Form.useForm();
  const [subs, setSubs] = useState<SubCompany[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [subForm] = Form.useForm();
  const [editingId, setEditingId] = useState<number | null>(null);

  // Thêm hoặc cập nhật công ty con
  const handleSubOk = () => {
    subForm.validateFields().then((values) => {
      if (editingId !== null) {
        setSubs((prev) => prev.map((s) => (s.id === editingId ? { ...s, ...values } : s)));
      } else {
        setSubs((prev) => [...prev, { ...values, id: Date.now() }]);
      }
      setModalOpen(false);
      setEditingId(null);
      subForm.resetFields();
    });
  };

  // Sửa công ty con
  const handleEdit = (record: SubCompany) => {
    setEditingId(record.id);
    subForm.setFieldsValue(record);
    setModalOpen(true);
  };

  // Xoá công ty con
  const handleDelete = (id: number) => {
    setSubs((prev) => prev.filter((s) => s.id !== id));
  };

  // Gửi form tạo công ty
  const handleFinish = (values: any) => {
    // TODO: Gửi API tạo công ty và các công ty con
    console.log("Tạo công ty:", values, subs);
  };

  const columns = [
    { title: "Tên công ty con", dataIndex: "name", key: "name" },
    { title: "Mã công ty", dataIndex: "code", key: "code" },
    {
      title: "Hành động",
      key: "action",
      render: (_: any, record: SubCompany) => (
        <Space>
          <Button size="small" onClick={() => handleEdit(record)}>
            Sửa
          </Button>
          <Popconfirm title="Xoá công ty con?" onConfirm={() => handleDelete(record.id)}>
            <Button size="small" danger>
              Xoá
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Card title={<Typography.Title level={3}>Tạo công ty</Typography.Title>}>
      <Form form={form} layout="vertical" onFinish={handleFinish}>
        <Form.Item label="Tên công ty" name="name" rules={[{ required: true, message: "Nhập tên công ty" }]}> <Input /> </Form.Item>
        <Form.Item label="Mã công ty" name="code" rules={[{ required: true, message: "Nhập mã công ty" }]}> <Input /> </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit">Tạo công ty</Button>
        </Form.Item>
      </Form>
      <Card
        title={<Space><span>Công ty con</span><Button type="primary" onClick={() => { setModalOpen(true); setEditingId(null); subForm.resetFields(); }}>Thêm công ty con</Button></Space>}
        style={{ marginTop: 32 }}
      >
        <Table columns={columns} dataSource={subs} rowKey="id" pagination={false} />
      </Card>
      <Modal
        title={editingId ? "Sửa công ty con" : "Thêm công ty con"}
        open={modalOpen}
        onOk={handleSubOk}
        onCancel={() => { setModalOpen(false); setEditingId(null); subForm.resetFields(); }}
        okText={editingId ? "Cập nhật" : "Thêm"}
        cancelText="Huỷ"
      >
        <Form form={subForm} layout="vertical">
          <Form.Item label="Tên công ty con" name="name" rules={[{ required: true, message: "Nhập tên công ty con" }]}> <Input /> </Form.Item>
          <Form.Item label="Mã công ty" name="code" rules={[{ required: true, message: "Nhập mã công ty" }]}> <Input /> </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}
