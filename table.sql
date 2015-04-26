create table users(
id integer not null primary key autoincrement,
p_num bigint(15) not null,
password varchar(50) not null
);
create table friends(
id integer not null primary key autoincrement,
p_num bigint(15) not null,
f_num bigint(15) not null
);
create table vehicle(
  id integer not null primary key autoincrement,
  p_num bigint(15) not null,
  num_plate varchar(50) not null,
  d_id bigint(15) not null,
  stamp varchar(255) not null
);
