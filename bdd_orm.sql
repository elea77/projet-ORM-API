create table user (
    id_user 		        int             not null AUTO_INCREMENT,
    username	            varchar(30)     not null,        
    email                   varchar(50)     not null,
    password                varchar(50)     not null,
    avatar                  varchar(200)    not null,
    date                    date            not null,
    constraint Pk_user primary key (id_user)
);


create table review (
    id_review 		        int             not null AUTO_INCREMENT,
    review	                text            not null,        
    date                    datetime        not null,
    id_user                 int             not null,
    constraint Pk_review primary key (id_review),
    constraint Fk_review_user foreign key (id_user) references user(id_user)
);


create table favorite_movie (
    id_favorite 		    int             not null AUTO_INCREMENT,
    id_movie	            int             not null,        
    id_user                 int             not null,
    constraint Pk_favorite primary key (id_favorite),
    constraint Fk_favorite_user foreign key (id_user) references user(id_user)
);