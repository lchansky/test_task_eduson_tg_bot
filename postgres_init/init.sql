CREATE TABLE public.photos (
	id bigserial NOT NULL,
	user_tg_id int8 NOT NULL,
	picsum_id int8 NOT NULL,
	author varchar NOT NULL,
	width int8 NOT NULL,
	height int8 NOT NULL,
	url varchar NOT NULL,
	download_url varchar NOT NULL,
	CONSTRAINT photos_pkey PRIMARY KEY (id)
);