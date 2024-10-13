from django.contrib.postgres.aggregates import ArrayAgg
from django.core import serializers
from django.db.models import Count, Prefetch, Q, Subquery
from django.http import JsonResponse
from django.views.generic.list import BaseListView

from config.settings import logger
from movies.models import (
    Filmwork,
    Genre,
    GenreFilmwork,
    Person,
    PersonFilmwork,
)


class MoviesListApi(BaseListView):
    model = Filmwork
    http_method_names = ["get"]  # Список методов, которые реализует обработчик

    def get_queryset(self):

        persons_queryset = Person.objects.all()
        persons_dict = {
            person.id: person.full_name for person in persons_queryset
        }
        logger.debug("persons_dict: \n%s\n", persons_dict)

        all_films = Filmwork.objects.all()

        films_genres = all_films.values("id").annotate(
            genres=ArrayAgg("genres__name", distinct=True),
        )
        films_actors = films_genres.annotate(
            actors=ArrayAgg(
                "personfilmwork",
                filter=Q(personfilmwork__role="actor"),
                distinct=True,
            ),
        )
        films_directors = films_actors.annotate(
            directors=ArrayAgg(
                "personfilmwork",
                filter=Q(personfilmwork__role="director"),
                distinct=True,
            ),
        )
        films_writers = films_directors.annotate(
            writers=ArrayAgg(
                "personfilmwork",
                filter=Q(personfilmwork__role="writer"),
                distinct=True,
            ),
        )

        films = films_writers.values(
            "id",
            "title",
            "description",
            "creation_date",
            "rating",
            "type",
            "genres",
            "actors",
            "directors",
            "writers",
        )
        logger.info("films[0]: \n%s\n", films[0])

        key_tuple = ("actors", "directors", "writers")
        for film in films:
            for key in key_tuple:
                names = []
                for person_id in film[key]:
                    names.append(persons_dict.get(person_id, None))
                film[key] = names
                logger.info("names: \n%s\n", names)

        return films

    def get_context_data(self, *, object_list=None, **kwargs):
        context = {
            "results": list(self.get_queryset()),
        }
        return context

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)
