from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import models


class DataBase:
    def __init__(self, db_url):
        engine = create_engine(db_url)
        models.Base.metadata.create_all(bind=engine)
        self.maker = sessionmaker(bind=engine)

    # def _get_of_create(self, session, model, u_field, u_value, **data):
    #     db_data = session.query(model).filter(u_field == data[u_value]).first()
    #     if not db_data:
    #         db_data = model(**data)
    #     return db_data
    #
    # def create_post(self, data):
    #     session = self.maker()
    #     author = self._get_of_create(session, models.Author, models.Author.url, 'url', **data['author'])
    #     post = self._get_of_create(session, models.Post, models.Post.url,
    #                                'url', **data['post_data'], author=author)
    #     post.tags.extend(map(lambda tag_data: self._get_of_create(session,
    #                                                               models.Tag,
    #                                                               models.Tag.url,
    #                                                               'url',
    #                                                               **tag_data), data['tags']))
    def _get_or_create(self, session, model, u_field, u_value, **data):
        db_data = session.query(model).filter(u_field == u_value).first()
        if not db_data:
            db_data = model(**data)
        return db_data

    def _get_or_create_comments(self, session, data: list):
        result = []
        for comment in data:
            comment_author = self._get_or_create(session,
                                                 models.Author,
                                                 models.Author.url,
                                                 comment['user_url'],
                                                 name=comment['user'],
                                                 url=comment['user_url'])
            comment_data = self._get_or_create(session,
                                               models.Comment,
                                               models.Comment.id,
                                               comment['id'],
                                               body=comment['text'],
                                               parent_id=comment['parent_id'],
                                               author=comment_author)
            result.append(comment_data)
        return result

    def create_post(self, data):
        session = self.maker()
        author = self._get_or_create(
            session, models.Author, models.Author.url, data["author"]["url"], **data["author"],
        )
        comments = self._get_or_create_comments(session, data['comments'])
        post = self._get_or_create(
            session, models.Post, models.Post.url, data["post_data"]['url'], **data["post_data"], author=author
        )
        tags = map(
                lambda tag_data: self._get_or_create(
                    session, models.Tag, models.Tag.url, tag_data['url'], **tag_data
                ),
                data["tags"],
            )
        post.tags.extend(tags)
        post.comments.extend(comments)
        session.add(post)
        try:
            session.commit()
        except Exception as exc:
            print(exc)
            session.rollback()
        finally:
            session.close()
