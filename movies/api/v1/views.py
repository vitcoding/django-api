from django.contrib.postgres.aggregates import ArrayAgg
from django.db import connection, reset_queries
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.list import BaseListView

from config.settings import logger
from movies.models import (
    Filmwork,
)  # Genre,; GenreFilmwork,; Person,; PersonFilmwork,


class MoviesListApi(BaseListView):
    model = Filmwork
    http_method_names = ["get"]

    def get_queryset(self):
        api_fields_base = (
            "id",
            "title",
            "description",
            "creation_date",
            "rating",
            "type",
            "genres",
        )

        films = Filmwork.objects.prefetch_related("genres", "persons")

        films_genres = films.values("id").annotate(
            genres=ArrayAgg("genres__name", distinct=True)
        )

        person_roles = ("actor", "director", "writer")
        role_fields = {}
        for key in person_roles:
            field = f"{key}s"
            role_fields[field] = ArrayAgg(
                f"persons__full_name",
                filter=Q(personfilmwork__role=key),
                distinct=True,
            )

        api_fields = list(api_fields_base)
        api_fields.extend(list(role_fields.keys()))
        logger.debug("\napi_fields: \n%s\n", api_fields)

        aggregated_fields = films_genres.annotate(**role_fields).values(
            *api_fields
        )
        return aggregated_fields

    def get_context_data(self, *, object_list=None, **kwargs):
        context = {"results": list(self.get_queryset())}
        logger.debug(
            "\nconnection.queries: \n%s\n",
            connection.queries,
        )
        logger.debug(
            "\nlen(connection.queries): \n%s\n",
            len(connection.queries),
        )
        return context

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)
