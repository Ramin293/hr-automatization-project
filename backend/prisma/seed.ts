import { EmployeeStatus, LeaveRequestStatus, PrismaClient, StaffingStatus } from '@prisma/client';

const prisma = new PrismaClient();
const uuid = (group: number, index: number) => `${group.toString().padStart(8, '0')}-0000-4000-8000-${index.toString().padStart(12, '0')}`;

const departments = [
  'Human Resources', 'Finance', 'Legal', 'Operations', 'Information Technology', 'Procurement', 'Security', 'Administration'
].map((name, index) => ({ id: uuid(1, index + 1), code: `DEP-${String(index + 1).padStart(2, '0')}`, name }));

const positionNames = [
  'Department Director', 'Team Lead', 'HR Specialist', 'Recruiter', 'Accountant', 'Financial Analyst', 'Legal Counsel', 'Operations Specialist',
  'Software Engineer', 'System Analyst', 'Procurement Specialist', 'Security Specialist', 'Office Administrator', 'Business Analyst', 'Project Manager'
];

async function seed() {
  await prisma.$transaction([
    prisma.outboxEvent.deleteMany(), prisma.auditEvent.deleteMany(), prisma.leaveRequest.deleteMany(), prisma.leaveBalance.deleteMany(),
    prisma.employee.deleteMany(), prisma.staffingPosition.deleteMany(), prisma.position.deleteMany(), prisma.department.deleteMany()
  ]);

  const positions = Array.from({ length: 45 }, (_, index) => ({
    id: uuid(2, index + 1),
    code: `POS-${String(index + 1).padStart(3, '0')}`,
    name: index < positionNames.length ? positionNames[index] : `Professional Grade ${index + 1}`
  }));
  const staffing = Array.from({ length: 200 }, (_, index) => ({
    id: uuid(3, index + 1),
    code: `STAFF-${String(index + 1).padStart(4, '0')}`,
    departmentId: departments[index % departments.length].id,
    positionId: positions[index % positions.length].id,
    status: index < 180 ? StaffingStatus.OCCUPIED : StaffingStatus.VACANT,
    validFrom: new Date('2024-01-01'),
    salaryMin: 250_000 + (index % 10) * 50_000,
    salaryMax: 500_000 + (index % 10) * 100_000
  }));

  await prisma.department.createMany({ data: departments });
  await prisma.position.createMany({ data: positions });
  await prisma.staffingPosition.createMany({ data: staffing });

  const employees = Array.from({ length: 180 }, (_, index) => {
    const number = index + 1;
    const departmentIndex = index % departments.length;
    const isManager = index < departments.length;
    const firstName = index === 0 ? 'Zarina' : index === 1 ? 'Madina' : `Employee${number}`;
    const lastName = index === 0 ? 'Sarsenova' : index === 1 ? 'Omarova' : `Demo${number}`;
    return {
      id: uuid(4, number),
      employeeNumber: `EMP-${String(number).padStart(5, '0')}`,
      status: index >= 170 ? EmployeeStatus.ON_LEAVE : EmployeeStatus.ACTIVE,
      fullName: `${firstName} ${lastName}`,
      initials: `${firstName[0]}${lastName[0]}`,
      workEmail: `employee.${number}@ertis.local`,
      workPhone: `+7701${String(1_000_000 + number).slice(-7)}`,
      departmentId: departments[departmentIndex].id,
      positionId: positions[index % positions.length].id,
      staffingPositionId: staffing[index].id,
      managerId: isManager ? null : uuid(4, departmentIndex + 1),
      legalEntityId: 'ERTIS-OPERATIONS',
      locationId: index % 3 === 0 ? 'ASTANA-HQ' : 'PAVLODAR-OFFICE',
      employmentType: 'FULL_TIME',
      workScheduleId: 'STANDARD-5-2',
      startDate: new Date(`202${index % 5}-0${(index % 9) + 1}-01`),
      probationEndDate: index >= 160 ? new Date('2026-12-31') : null,
      personnelFileCompleteness: 75 + (index % 26),
      salary: 350_000 + (index % 20) * 35_000,
      candidateGroups: index % 4 === 0 ? ['SUCCESSION_POOL'] : [],
      skills: [`skill-${(index % 12) + 1}`, `skill-${(index % 7) + 13}`],
      createdBy: 'seed',
      updatedBy: 'seed'
    };
  });
  await prisma.employee.createMany({ data: employees });
  await prisma.leaveBalance.createMany({ data: employees.map((employee, index) => ({
    id: uuid(5, index + 1), employeeId: employee.id, leaveType: 'ANNUAL_PAID', year: 2026, available: 28, reserved: 0, used: 0
  })) });

  await prisma.leaveRequest.createMany({ data: Array.from({ length: 35 }, (_, index) => {
    const employee = employees[index + 10];
    const startDay = (index % 20) + 1;
    return {
      id: uuid(6, index + 1),
      employeeId: employee.id,
      leaveType: 'ANNUAL_PAID',
      startDate: new Date(`2026-09-${String(startDay).padStart(2, '0')}`),
      endDate: new Date(`2026-09-${String(startDay + 2).padStart(2, '0')}`),
      requestedDuration: 3,
      substituteEmployeeId: employees[index + 50].id,
      comment: 'Seeded annual leave request',
      balanceSnapshot: 28,
      status: index % 2 === 0 ? LeaveRequestStatus.MANAGER_REVIEW : LeaveRequestStatus.HR_REVIEW,
      documentId: `seed-document-${index + 1}`,
      documentNumber: `HR-LV-2026-${String(index + 1).padStart(4, '0')}`,
      workflowInstanceId: `seed-workflow-${index + 1}`,
      workflowStep: index % 2 === 0 ? 'MANAGER_REVIEW' : 'HR_REVIEW',
      auditCorrelationId: `seed-correlation-${index + 1}`,
      idempotencyKey: `seed-leave-${String(index + 1).padStart(4, '0')}`,
      createdBy: 'seed',
      updatedBy: 'seed'
    };
  }) });

  process.stdout.write(`${JSON.stringify({ event: 'seed.complete', departments: departments.length, positions: positions.length, staffingPositions: staffing.length, employees: employees.length, leaveRequests: 35 })}\n`);
}

void seed()
  .catch((error: unknown) => {
    process.stderr.write(`${JSON.stringify({ event: 'seed.failed', error: error instanceof Error ? error.message : 'unknown error' })}\n`);
    process.exitCode = 1;
  })
  .finally(async () => prisma.$disconnect());
