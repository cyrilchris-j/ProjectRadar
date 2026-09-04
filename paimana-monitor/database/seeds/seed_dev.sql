-- =============================================================================
-- PAIMANA — Development Seed Data
-- ⚠️  SYNTHETIC DATA — NOT OFFICIAL PAIMANA/OCMS DATA ⚠️
-- For development and demonstration purposes only.
-- All project names, IDs, costs, and dates are fictitious.
-- =============================================================================

-- Default admin user (password: Admin@1234 — change before any deployment)
INSERT INTO users (id, email, full_name, password_hash, role, is_active) VALUES
  ('a0000000-0000-0000-0000-000000000001', 'admin@paimana.gov.in',   'System Administrator', '$2b$12$Iz6qzhUk1XdgkZ4y4K5ADuMP2bR7o4o0xFyhKQLJXfglUuSNA5moW', 'admin',   TRUE),
  ('a0000000-0000-0000-0000-000000000002', 'analyst@paimana.gov.in', 'Data Analyst',          '$2b$12$Iz6qzhUk1XdgkZ4y4K5ADuMP2bR7o4o0xFyhKQLJXfglUuSNA5moW',          'analyst', TRUE),
  ('a0000000-0000-0000-0000-000000000003', 'officer@paimana.gov.in', 'Field Officer',          '$2b$12$Iz6qzhUk1XdgkZ4y4K5ADuMP2bR7o4o0xFyhKQLJXfglUuSNA5moW',          'officer', TRUE),
  ('a0000000-0000-0000-0000-000000000004', 'viewer@paimana.gov.in',  'Report Viewer',          '$2b$12$Iz6qzhUk1XdgkZ4y4K5ADuMP2bR7o4o0xFyhKQLJXfglUuSNA5moW',          'viewer',  TRUE);

-- Organizations
INSERT INTO organizations (id, name, code, organization_type) VALUES
  ('b0000000-0000-0000-0000-000000000001', 'Ministry of Road Transport & Highways', 'MoRTH',  'Ministry'),
  ('b0000000-0000-0000-0000-000000000002', 'Ministry of Railways',                  'MoR',    'Ministry'),
  ('b0000000-0000-0000-0000-000000000003', 'Ministry of Power',                     'MoP',    'Ministry'),
  ('b0000000-0000-0000-0000-000000000004', 'Ministry of Petroleum & Natural Gas',   'MoPNG',  'Ministry'),
  ('b0000000-0000-0000-0000-000000000005', 'National Highways Authority of India',  'NHAI',   'Agency'),
  ('b0000000-0000-0000-0000-000000000006', 'Indian Railways',                       'IR',     'Agency');

-- =============================================================================
-- PROJECTS (30 synthetic projects across 5 sectors, 6 states)
-- =============================================================================
INSERT INTO projects (
  id, project_id, project_name, ministry, sector, state,
  original_cost, revised_cost,
  original_start_date, original_completion_date, revised_completion_date,
  current_status, implementing_agency
) VALUES
  -- Roads (healthy)
  ('c0001000-0000-0000-0000-000000000001','700001','NH-48 Four-Laning Package 1','Ministry of Road Transport & Highways','Roads','Tamil Nadu',28500.00,28500.00,'2023-04-01','2026-03-31','2026-03-31','ongoing','NHAI'),
  ('c0002000-0000-0000-0000-000000000002','700002','NH-44 Bypass Corridor','Ministry of Road Transport & Highways','Roads','Andhra Pradesh',42000.00,45200.00,'2022-10-01','2025-09-30','2026-06-30','ongoing','NHAI'),
  ('c0003000-0000-0000-0000-000000000003','700003','State Highway Widening SH-12','Ministry of Road Transport & Highways','Roads','Karnataka',8900.00,9800.00,'2024-01-01','2026-12-31','2027-06-30','ongoing','PWD Karnataka'),
  ('c0004000-0000-0000-0000-000000000004','700004','Ring Road Phase II','Ministry of Road Transport & Highways','Roads','Maharashtra',67000.00,71500.00,'2021-06-01','2025-05-31','2026-11-30','ongoing','MSRDC'),
  ('c0005000-0000-0000-0000-000000000005','700005','Rural Connectivity Package RC-07','Ministry of Road Transport & Highways','Roads','Rajasthan',3200.00,3200.00,'2025-01-01','2026-12-31','2026-12-31','ongoing','PWD Rajasthan'),

  -- Roads (at risk)
  ('c0006000-0000-0000-0000-000000000006','700006','NH-66 Coastal Expressway','Ministry of Road Transport & Highways','Roads','Kerala',95000.00,114000.00,'2020-03-01','2024-02-29','2027-03-31','ongoing','NHAI'),
  ('c0007000-0000-0000-0000-000000000007','700007','Mountain Highway Package MH-03','Ministry of Road Transport & Highways','Roads','Himachal Pradesh',18500.00,24000.00,'2021-09-01','2025-08-31','2027-02-28','stalled','BRO'),

  -- Railways
  ('c0008000-0000-0000-0000-000000000008','700008','New Railway Line Doubling Phase 1','Ministry of Railways','Railways','Madhya Pradesh',54000.00,54000.00,'2023-01-01','2026-12-31','2026-12-31','ongoing','Indian Railways'),
  ('c0009000-0000-0000-0000-000000000009','700009','Station Redevelopment Bhopal','Ministry of Railways','Railways','Madhya Pradesh',1200.00,1350.00,'2024-04-01','2026-03-31','2026-09-30','ongoing','Indian Railways'),
  ('c0010000-0000-0000-0000-000000000010','700010','Freight Corridor Extension FC-02','Ministry of Railways','Railways','Uttar Pradesh',185000.00,198000.00,'2019-10-01','2024-09-30','2026-12-31','ongoing','DFCCIL'),
  ('c0011000-0000-0000-0000-000000000011','700011','Metro Rail Phase 3 Corridor A','Ministry of Railways','Railways','Karnataka',82000.00,95000.00,'2021-04-01','2025-03-31','2027-06-30','ongoing','BMRCL'),

  -- Power
  ('c0012000-0000-0000-0000-000000000012','700012','Solar Power Plant 500MW','Ministry of Power','Power','Rajasthan',62000.00,62000.00,'2024-06-01','2026-05-31','2026-05-31','ongoing','SECI'),
  ('c0013000-0000-0000-0000-000000000013','700013','Transmission Line 765kV','Ministry of Power','Power','Uttar Pradesh',28000.00,31000.00,'2022-07-01','2025-06-30','2026-06-30','ongoing','PowerGrid'),
  ('c0014000-0000-0000-0000-000000000014','700014','Hydro Power Project 200MW','Ministry of Power','Power','Himachal Pradesh',95000.00,118000.00,'2018-04-01','2024-03-31','2028-03-31','stalled','SJVN'),
  ('c0015000-0000-0000-0000-000000000015','700015','Rural Electrification Package RE-11','Ministry of Power','Power','Jharkhand',4500.00,4700.00,'2024-10-01','2026-09-30','2026-12-31','ongoing','JBVNL'),

  -- Petroleum
  ('c0016000-0000-0000-0000-000000000016','700016','LPG Pipeline West Coast','Ministry of Petroleum & Natural Gas','Petroleum','Maharashtra',34000.00,37500.00,'2022-01-01','2025-12-31','2026-09-30','ongoing','GAIL'),
  ('c0017000-0000-0000-0000-000000000017','700017','Petroleum Refinery Expansion','Ministry of Petroleum & Natural Gas','Petroleum','Gujarat',245000.00,282000.00,'2019-06-01','2024-05-31','2027-05-31','ongoing','HPCL'),
  ('c0018000-0000-0000-0000-000000000018','700018','CNG Station Network Phase 2','Ministry of Petroleum & Natural Gas','Petroleum','Tamil Nadu',8200.00,8200.00,'2025-01-01','2026-12-31','2026-12-31','ongoing','IGL'),

  -- Water / Urban
  ('c0019000-0000-0000-0000-000000000019','700019','Urban Water Supply Modernisation','Ministry of Jal Shakti','Water','Andhra Pradesh',12500.00,13800.00,'2023-06-01','2026-05-31','2026-11-30','ongoing','APSPDCL'),
  ('c0020000-0000-0000-0000-000000000020','700020','River Cleaning Project Phase I','Ministry of Jal Shakti','Water','Uttar Pradesh',28000.00,34000.00,'2021-01-01','2025-12-31','2027-06-30','ongoing','NMCG'),

  -- Additional projects for volume
  ('c0021000-0000-0000-0000-000000000021','700021','Airport Runway Extension','Ministry of Civil Aviation','Aviation','Tamil Nadu',18000.00,18000.00,'2024-09-01','2026-08-31','2026-08-31','ongoing','AAI'),
  ('c0022000-0000-0000-0000-000000000022','700022','Port Modernisation Phase 3','Ministry of Ports','Ports','Maharashtra',55000.00,62000.00,'2021-03-01','2025-02-28','2026-08-31','ongoing','JPA'),
  ('c0023000-0000-0000-0000-000000000023','700023','Industrial Corridor Connectivity','Ministry of Commerce','Industrial','Gujarat',38000.00,38000.00,'2024-01-01','2027-12-31','2027-12-31','ongoing','DMIC'),
  ('c0024000-0000-0000-0000-000000000024','700024','Smart City Infrastructure Pune','Ministry of Housing','Urban','Maharashtra',15000.00,16500.00,'2023-04-01','2026-03-31','2026-09-30','ongoing','PMC'),
  ('c0025000-0000-0000-0000-000000000025','700025','Irrigation Canal Modernisation','Ministry of Jal Shakti','Irrigation','Rajasthan',9800.00,11200.00,'2022-10-01','2025-09-30','2026-09-30','ongoing','RAJWAS'),
  ('c0026000-0000-0000-0000-000000000026','700026','Border Area Road Package BAR-05','Ministry of Road Transport & Highways','Roads','Rajasthan',14500.00,16800.00,'2021-07-01','2025-06-30','2026-12-31','ongoing','BRO'),
  ('c0027000-0000-0000-0000-000000000027','700027','Gas Grid Expansion Phase 4','Ministry of Petroleum & Natural Gas','Petroleum','Karnataka',22000.00,22000.00,'2024-04-01','2027-03-31','2027-03-31','ongoing','GAIL'),
  ('c0028000-0000-0000-0000-000000000028','700028','Rail Over Bridge Package ROB-12','Ministry of Railways','Railways','Uttar Pradesh',4200.00,4600.00,'2023-07-01','2025-06-30','2026-03-31','ongoing','Indian Railways'),
  ('c0029000-0000-0000-0000-000000000029','700029','Thermal Power Upgrade TPP-4','Ministry of Power','Power','Maharashtra',48000.00,56000.00,'2020-01-01','2024-12-31','2027-06-30','stalled','MAHAGENCO'),
  ('c0030000-0000-0000-0000-000000000030','700030','Bridge Construction Package BC-22','Ministry of Road Transport & Highways','Roads','Andhra Pradesh',7200.00,7200.00,'2025-04-01','2027-03-31','2027-03-31','ongoing','NHAI');

-- =============================================================================
-- PROJECT SNAPSHOTS — April 2026
-- (Synthetic monthly observations)
-- =============================================================================
INSERT INTO project_snapshots (project_id, report_month, physical_progress, planned_progress, cumulative_expenditure, current_cost, current_completion_date, current_status) VALUES
  -- Roads
  ((SELECT id FROM projects WHERE project_id='700001'),'2026-04-01',76.20,74.00,21200.00,28500.00,'2026-03-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700002'),'2026-04-01',58.40,70.00,31000.00,45200.00,'2026-06-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700003'),'2026-04-01',30.10,28.00,2500.00,9800.00,'2027-06-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700004'),'2026-04-01',51.80,60.00,43000.00,71500.00,'2026-11-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700005'),'2026-04-01',28.00,25.00,820.00,3200.00,'2026-12-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700006'),'2026-04-01',38.50,75.00,86000.00,114000.00,'2027-03-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700007'),'2026-04-01',22.00,60.00,14800.00,24000.00,'2027-02-28','stalled'),
  -- Railways
  ((SELECT id FROM projects WHERE project_id='700008'),'2026-04-01',42.00,40.00,21600.00,54000.00,'2026-12-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700009'),'2026-04-01',72.00,80.00,1050.00,1350.00,'2026-09-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700010'),'2026-04-01',55.20,70.00,138000.00,198000.00,'2026-12-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700011'),'2026-04-01',31.00,42.00,42000.00,95000.00,'2027-06-30','ongoing'),
  -- Power
  ((SELECT id FROM projects WHERE project_id='700012'),'2026-04-01',82.00,80.00,49000.00,62000.00,'2026-05-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700013'),'2026-04-01',61.00,58.00,17800.00,31000.00,'2026-06-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700014'),'2026-04-01',18.00,60.00,52000.00,118000.00,'2028-03-31','stalled'),
  ((SELECT id FROM projects WHERE project_id='700015'),'2026-04-01',45.00,42.00,2050.00,4700.00,'2026-12-31','ongoing'),
  -- Petroleum
  ((SELECT id FROM projects WHERE project_id='700016'),'2026-04-01',68.00,65.00,24500.00,37500.00,'2026-09-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700017'),'2026-04-01',41.00,65.00,198000.00,282000.00,'2027-05-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700018'),'2026-04-01',22.00,20.00,1400.00,8200.00,'2026-12-31','ongoing'),
  -- Water
  ((SELECT id FROM projects WHERE project_id='700019'),'2026-04-01',55.00,52.00,7800.00,13800.00,'2026-11-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700020'),'2026-04-01',28.00,50.00,16000.00,34000.00,'2027-06-30','ongoing'),
  -- Others
  ((SELECT id FROM projects WHERE project_id='700021'),'2026-04-01',58.00,55.00,9900.00,18000.00,'2026-08-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700022'),'2026-04-01',62.00,70.00,42000.00,62000.00,'2026-08-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700023'),'2026-04-01',20.00,18.00,6800.00,38000.00,'2027-12-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700024'),'2026-04-01',67.00,72.00,11200.00,16500.00,'2026-09-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700025'),'2026-04-01',42.00,50.00,5100.00,11200.00,'2026-09-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700026'),'2026-04-01',35.00,55.00,9800.00,16800.00,'2026-12-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700027'),'2026-04-01',18.00,16.00,3200.00,22000.00,'2027-03-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700028'),'2026-04-01',72.00,75.00,3400.00,4600.00,'2026-03-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700029'),'2026-04-01',25.00,60.00,34000.00,56000.00,'2027-06-30','stalled'),
  ((SELECT id FROM projects WHERE project_id='700030'),'2026-04-01',8.00,7.00,480.00,7200.00,'2027-03-31','ongoing');

-- =============================================================================
-- PROJECT SNAPSHOTS — May 2026
-- =============================================================================
INSERT INTO project_snapshots (project_id, report_month, physical_progress, planned_progress, cumulative_expenditure, current_cost, current_completion_date, current_status) VALUES
  ((SELECT id FROM projects WHERE project_id='700001'),'2026-05-01',78.90,79.00,22500.00,28500.00,'2026-03-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700002'),'2026-05-01',60.10,75.00,33500.00,45200.00,'2026-06-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700003'),'2026-05-01',33.50,33.00,2950.00,9800.00,'2027-06-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700004'),'2026-05-01',53.00,65.00,46000.00,71500.00,'2026-11-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700005'),'2026-05-01',34.00,32.00,1050.00,3200.00,'2026-12-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700006'),'2026-05-01',39.80,80.00,90000.00,114000.00,'2027-03-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700007'),'2026-05-01',22.80,63.00,15200.00,24000.00,'2027-02-28','stalled'),
  ((SELECT id FROM projects WHERE project_id='700008'),'2026-05-01',46.00,46.00,23800.00,54000.00,'2026-12-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700009'),'2026-05-01',78.00,88.00,1150.00,1350.00,'2026-09-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700010'),'2026-05-01',57.80,74.00,142000.00,198000.00,'2026-12-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700011'),'2026-05-01',33.50,46.00,45000.00,95000.00,'2027-06-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700012'),'2026-05-01',88.00,87.00,52000.00,62000.00,'2026-05-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700013'),'2026-05-01',64.00,63.00,19200.00,31000.00,'2026-06-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700014'),'2026-05-01',18.50,62.00,53000.00,118000.00,'2028-03-31','stalled'),
  ((SELECT id FROM projects WHERE project_id='700015'),'2026-05-01',50.00,50.00,2350.00,4700.00,'2026-12-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700016'),'2026-05-01',71.00,70.00,26000.00,37500.00,'2026-09-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700017'),'2026-05-01',42.50,68.00,204000.00,282000.00,'2027-05-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700018'),'2026-05-01',28.00,28.00,1950.00,8200.00,'2026-12-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700019'),'2026-05-01',59.00,58.00,8500.00,13800.00,'2026-11-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700020'),'2026-05-01',29.50,53.00,17200.00,34000.00,'2027-06-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700021'),'2026-05-01',63.00,62.00,10800.00,18000.00,'2026-08-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700022'),'2026-05-01',65.00,74.00,45000.00,62000.00,'2026-08-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700023'),'2026-05-01',23.00,22.00,7800.00,38000.00,'2027-12-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700024'),'2026-05-01',70.00,77.00,12000.00,16500.00,'2026-09-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700025'),'2026-05-01',45.00,55.00,5800.00,11200.00,'2026-09-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700026'),'2026-05-01',37.00,58.00,10500.00,16800.00,'2026-12-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700027'),'2026-05-01',22.00,21.00,4100.00,22000.00,'2027-03-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700028'),'2026-05-01',80.00,85.00,3900.00,4600.00,'2026-03-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700029'),'2026-05-01',25.50,63.00,35000.00,56000.00,'2027-06-30','stalled'),
  ((SELECT id FROM projects WHERE project_id='700030'),'2026-05-01',12.00,12.00,850.00,7200.00,'2027-03-31','ongoing');

-- =============================================================================
-- PROJECT SNAPSHOTS — June 2026
-- =============================================================================
INSERT INTO project_snapshots (project_id, report_month, physical_progress, planned_progress, cumulative_expenditure, current_cost, current_completion_date, current_status) VALUES
  ((SELECT id FROM projects WHERE project_id='700001'),'2026-06-01',81.50,83.00,23800.00,28500.00,'2026-03-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700002'),'2026-06-01',62.00,80.00,36200.00,45200.00,'2026-06-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700003'),'2026-06-01',37.20,38.00,3450.00,9800.00,'2027-06-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700004'),'2026-06-01',55.10,70.00,49500.00,71500.00,'2026-11-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700005'),'2026-06-01',40.00,39.00,1280.00,3200.00,'2026-12-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700006'),'2026-06-01',40.20,85.00,94000.00,114000.00,'2027-03-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700007'),'2026-06-01',23.10,66.00,15500.00,24000.00,'2027-02-28','stalled'),
  ((SELECT id FROM projects WHERE project_id='700008'),'2026-06-01',50.00,52.00,26500.00,54000.00,'2026-12-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700009'),'2026-06-01',84.00,95.00,1250.00,1350.00,'2026-09-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700010'),'2026-06-01',59.86,78.00,148000.00,198000.00,'2026-12-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700011'),'2026-06-01',36.00,50.00,49000.00,95000.00,'2027-06-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700012'),'2026-06-01',95.00,95.00,56000.00,62000.00,'2026-05-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700013'),'2026-06-01',67.00,68.00,20800.00,31000.00,'2026-06-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700014'),'2026-06-01',18.80,64.00,54500.00,118000.00,'2028-03-31','stalled'),
  ((SELECT id FROM projects WHERE project_id='700015'),'2026-06-01',55.00,58.00,2700.00,4700.00,'2026-12-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700016'),'2026-06-01',74.00,75.00,27800.00,37500.00,'2026-09-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700017'),'2026-06-01',44.00,71.00,210000.00,282000.00,'2027-05-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700018'),'2026-06-01',35.00,36.00,2600.00,8200.00,'2026-12-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700019'),'2026-06-01',63.00,64.00,9200.00,13800.00,'2026-11-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700020'),'2026-06-01',31.00,56.00,18500.00,34000.00,'2027-06-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700021'),'2026-06-01',68.00,68.00,11600.00,18000.00,'2026-08-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700022'),'2026-06-01',68.00,78.00,48500.00,62000.00,'2026-08-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700023'),'2026-06-01',26.00,26.00,8900.00,38000.00,'2027-12-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700024'),'2026-06-01',74.00,83.00,13000.00,16500.00,'2026-09-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700025'),'2026-06-01',48.00,60.00,6500.00,11200.00,'2026-09-30','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700026'),'2026-06-01',39.00,62.00,11200.00,16800.00,'2026-12-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700027'),'2026-06-01',26.00,26.00,5200.00,22000.00,'2027-03-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700028'),'2026-06-01',87.00,95.00,4300.00,4600.00,'2026-03-31','ongoing'),
  ((SELECT id FROM projects WHERE project_id='700029'),'2026-06-01',26.00,66.00,36500.00,56000.00,'2027-06-30','stalled'),
  ((SELECT id FROM projects WHERE project_id='700030'),'2026-06-01',16.00,17.00,1200.00,7200.00,'2027-03-31','ongoing');

-- =============================================================================
-- SAMPLE MILESTONES
-- =============================================================================
INSERT INTO milestones (project_id, milestone_name, planned_date, actual_date, status) VALUES
  ((SELECT id FROM projects WHERE project_id='700001'),'Land Acquisition Complete','2023-09-01','2023-09-15','completed'),
  ((SELECT id FROM projects WHERE project_id='700001'),'Subgrade Completion 50%','2025-03-01','2025-04-10','completed'),
  ((SELECT id FROM projects WHERE project_id='700001'),'Pavement Layer 1 Complete','2026-01-01',NULL,'delayed'),

  ((SELECT id FROM projects WHERE project_id='700006'),'Land Acquisition Complete','2020-09-01','2022-06-01','completed'),
  ((SELECT id FROM projects WHERE project_id='700006'),'Foundation Work Complete','2021-06-01',NULL,'missed'),
  ((SELECT id FROM projects WHERE project_id='700006'),'Bridge Structures Complete','2022-12-01',NULL,'missed'),
  ((SELECT id FROM projects WHERE project_id='700006'),'Pavement Phase 1','2023-12-01',NULL,'missed'),

  ((SELECT id FROM projects WHERE project_id='700007'),'Site Clearance','2022-01-01','2022-03-01','completed'),
  ((SELECT id FROM projects WHERE project_id='700007'),'Foundation Complete','2022-12-01',NULL,'missed'),
  ((SELECT id FROM projects WHERE project_id='700007'),'Superstructure 50%','2024-06-01',NULL,'missed'),

  ((SELECT id FROM projects WHERE project_id='700012'),'Civil Works Complete','2025-12-01','2026-01-15','completed'),
  ((SELECT id FROM projects WHERE project_id='700012'),'Equipment Installation','2026-03-01','2026-04-01','completed'),
  ((SELECT id FROM projects WHERE project_id='700012'),'Grid Synchronisation','2026-05-31',NULL,'pending');

-- =============================================================================
-- NOTE: Actual users' passwords in production MUST be properly hashed.
-- These seed records use placeholder hashes and must be replaced before use.
-- =============================================================================
