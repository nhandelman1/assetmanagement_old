use am_dev;
show tables;

SET SQL_SAFE_UPDATES = 1;
SET FOREIGN_KEY_CHECKS = 1;

select * from real_estate;
select * from service_provider;
select * from real_property_values;
select * from mysunpower_hourly_data order by dt desc;
select * from electric_bill_data;
select * from electric_data;
select * from estimate_notes order by service_provider_id, note_order;
select start_date, end_date from natgas_bill_data where is_actual=1;
select * from natgas_bill_data;
select * from natgas_bill_data where start_date = '2023-03-31';
select * from natgas_data;
select * from simple_bill_data;
select * from solar_bill_data;
select * from mortgage_bill_data;
select * from depreciation_bill_data;

insert into estimate_notes (real_estate_id, provider, note_type, note, note_order) values 
(1, 'NationalGrid', 'wna_low_rate', 
'https://www.nationalgridus.com/Long-Island-NY-Home/Bills-Meters-and-Rates/Weather-Normalization-Adjustment -> From Date and To Date matching bill dates -> SC1B column 4-50 therms (or lowest therm level).
 WNA is added to previously entered DRA to get final DRA.', 
1);