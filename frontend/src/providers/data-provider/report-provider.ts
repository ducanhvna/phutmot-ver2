import { faker } from "@faker-js/faker";

export interface Report {
  id: string;
  title: string;
  employee_id: number;
  date: string;
  shift: string;
  minutes: number;
  is_complete: boolean;
}

const generateReports = (): Report[] => {
  return Array.from({ length: 200 }, (_, i) => ({
    id: faker.string.uuid(),
    title: `Báo cáo công việc ${i + 1}`,
    employee_id: faker.number.int({ min: 1, max: 40 }),
    date: faker.date.recent().toISOString().split("T")[0],
    shift: faker.helpers.arrayElement(["Ca sáng", "Ca chiều", "Ca tối"]),
    minutes: faker.number.int({ min: 240, max: 480 }),
    is_complete: faker.datatype.boolean(),
  }));
};

export const mockReports = generateReports();
export default mockReports;
