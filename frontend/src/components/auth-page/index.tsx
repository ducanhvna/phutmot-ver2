"use client";
import React from "react";
import { useLogin, useRegister } from "@refinedev/core";
import {
  Row,
  Col,
  Layout as AntdLayout,
  Card,
  Typography,
  Form,
  Input,
  Button,
  Checkbox,
} from "antd";
import Image from "next/image";
import "./styles.css";

const { Text, Title } = Typography;

export interface AuthPageProps {
  type?: "login" | "forgotPassword" | "register";
}

export const AuthPage: React.FC<AuthPageProps> = ({ type = "login" }) => {
  const [form] = Form.useForm();
  const { mutate: login } = useLogin();
  const { mutate: register } = useRegister();

  const CardTitle = (
    <Title level={3} className="title">
      {type === "forgotPassword"
        ? "Reset Your Password"
        : type === "register"
        ? "Create a New Account"
        : "Sign in to Your Account"}
    </Title>
  );

  return (
    <AntdLayout className="layout">
      <Row justify="center" align="middle" style={{ height: "100vh" }}>
        <Col xs={22}>
          <div className="container">
            <div className="imageContainer">
              <Image src="/refine.svg" alt="Refine Logo" width={150} height={50} />
            </div>
            <Card title={CardTitle} headStyle={{ borderBottom: 0 }}>
              <Form
                layout="vertical"
                form={form}
                onFinish={(values) => {
                  if (type === "register") {
                    register(values);
                  } else if (type === "forgotPassword") {
                    console.log("Forgot password request:", values);
                  } else {
                    login(values);
                  }
                }}
                requiredMark={false}
              >
                {type === "forgotPassword" && (
                  <Form.Item
                    name="email"
                    label="Email"
                    rules={[{ required: true, message: "Vui lòng nhập email!" }]}
                  >
                    <Input size="large" placeholder="Enter your email" />
                  </Form.Item>
                )}

                {type === "register" && (
                  <>
                    <Form.Item
                      name="username"
                      label="Username"
                      rules={[{ required: true, message: "Vui lòng nhập username!" }]}
                    >
                      <Input size="large" placeholder="Username" />
                    </Form.Item>
                    <Form.Item
                      name="email"
                      label="Email"
                      rules={[{ required: true, message: "Vui lòng nhập email!" }, { type: "email", message: "Email không hợp lệ!" }]}
                    >
                      <Input size="large" placeholder="Enter your email" />
                    </Form.Item>
                    <Form.Item
                      name="password"
                      label="Password"
                      rules={[{ required: true, message: "Vui lòng nhập mật khẩu!" }]}
                    >
                      <Input type="password" placeholder="●●●●●●●●" size="large" />
                    </Form.Item>
                    <Form.Item
                      name="confirmPassword"
                      label="Confirm Password"
                      dependencies={["password"]}
                      rules={[
                        { required: true, message: "Vui lòng nhập lại mật khẩu!" },
                        ({ getFieldValue }) => ({
                          validator(_, value) {
                            if (!value || getFieldValue("password") === value) {
                              return Promise.resolve();
                            }
                            return Promise.reject(new Error("Mật khẩu không khớp!"));
                          },
                        }),
                      ]}
                    >
                      <Input type="password" placeholder="●●●●●●●●" size="large" />
                    </Form.Item>
                  </>
                )}

                {type === "login" && (
                  <>
                    <Form.Item
                      name="username"
                      label="Username"
                      rules={[{ required: true, message: "Vui lòng nhập username!" }]}
                    >
                      <Input size="large" placeholder="Username" />
                    </Form.Item>
                    <Form.Item
                      name="password"
                      label="Password"
                      rules={[{ required: true, message: "Vui lòng nhập mật khẩu!" }]}
                      style={{ marginBottom: "12px" }}
                    >
                      <Input type="password" placeholder="●●●●●●●●" size="large" />
                    </Form.Item>
                    <div style={{ marginBottom: "12px" }}>
                      <Form.Item name="remember" valuePropName="checked" noStyle>
                        <Checkbox style={{ fontSize: "12px" }}>Remember me</Checkbox>
                      </Form.Item>
                      <a style={{ float: "right", fontSize: "12px" }} href="/forgot-password">
                        Forgot password?
                      </a>
                    </div>
                  </>
                )}

                <Button type="primary" size="large" htmlType="submit" block>
                  {type === "forgotPassword" ? "Reset Password" : type === "register" ? "Create Account" : "Sign in"}
                </Button>
              </Form>

              {type === "login" && (
                <div style={{ marginTop: 8 }}>
                  <Text style={{ fontSize: 12 }}>
                    Don’t have an account?{" "}
                    <a href="/register" style={{ fontWeight: "bold" }}>
                      Sign up
                    </a>
                  </Text>
                </div>
              )}
            </Card>
          </div>
        </Col>
      </Row>
    </AntdLayout>
  );
};
