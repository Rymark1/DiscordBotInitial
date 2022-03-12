CREATE TABLE IF NOT EXISTS guilds (
    GuildID integer PRIMARY KEY,
    Prefix text DEFAULT "+"
);

CREATE TABLE IF NOT EXISTS exp (
	UserID integer PRIMARY KEY,
	XP integer DEFAULT 0,
	Level integer DEFAULT 0,
	XPLock text DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS craps_bank (
	UserID integer PRIMARY KEY,
	bankRoll float DEFAULT 0
);

CREATE TABLE IF NOT EXISTS craps_board (
	n_UserID integer PRIMARY KEY,
	i_pass integer DEFAULT 0,
	i_dont integer DEFAULT 0,
	i_pass_odds integer DEFAULT 0,
	i_dont_odds integer DEFAULT 0,
	i_place_4 integer DEFAULT 0,
    i_place_5 integer DEFAULT 0,
    i_place_6 integer DEFAULT 0,
    i_place_8 integer DEFAULT 0,
    i_place_9 integer DEFAULT 0,
    i_place_10 integer DEFAULT 0,
    i_hard_4 integer DEFAULT 0,
    i_hard_5 integer DEFAULT 0,
    i_hard_6 integer DEFAULT 0,
    i_hard_8 integer DEFAULT 0,
    i_hard_10 integer DEFAULT 0,
    i_horn_2 integer DEFAULT 0,
    i_horn_3 integer DEFAULT 0,
    i_horn_11 integer DEFAULT 0,
    i_horn_12 integer DEFAULT 0,
    i_horny integer DEFAULT 0,
    i_field integer DEFAULT 0
);

CREATE TABLE IF NOT EXISTS craps_current (
	n_dummy integer PRIMARY KEY,
	b_shooter integer DEFAULT 0,
    i_point integer DEFAULT 0,
    i_roll_nbr integer DEFAULT 0
);