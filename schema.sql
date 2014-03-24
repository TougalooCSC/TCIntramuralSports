drop table if exists teams;
create table teams (
	id integer primary key autoincrement,
	name text not null
);
drop table if exists players;
create table players (
	id integer primary key autoincrement,
	firstname text not null,
	lastname text not null,
	playernumber integer,
	position integer,
	teamId integer 

);