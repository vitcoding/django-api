from django.contrib.postgres.aggregates import ArrayAgg
from django.core.paginator import Paginator
from django.db import connection
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
    paginate_by = 50

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

    # def validate_page(self, page, num_pages):
    #     if isinstance(page, int):
    #         if page < 1:
    #             return 1
    #         if page > num_pages:
    #             return num_pages

    #     return page

    def get_context_data(self, *, object_list=None, **kwargs):
        films_queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            films_queryset, self.paginate_by
        )

        logger.debug(
            "\npaginator: \n%s\n\npage: \n%s\n\nqueryset: \n%s\npage.number: \n%s\n\n",
            paginator,
            paginator.page,
            queryset,
            page.number,
        )

        # current_page = page.number
        # current_page = self.validate_page(page.number, paginator.num_pages)

        context = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": (
                page.previous_page_number() if page.has_previous() else None
            ),
            "next": (page.next_page_number() if page.has_next() else None),
            "results": list(queryset),
        }

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
