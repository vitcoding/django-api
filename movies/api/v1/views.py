from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from movies.models import Filmwork


class MoviesApiMixin:
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
                "persons__full_name",
                filter=Q(personfilmwork__role=key),
                distinct=True,
            )

        api_fields = list(api_fields_base)
        api_fields.extend(list(role_fields.keys()))

        aggregated_fields = films_genres.annotate(**role_fields).values(
            *api_fields
        )
        return aggregated_fields

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        films_queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            films_queryset, self.paginate_by
        )

        context = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": (
                page.previous_page_number() if page.has_previous() else None
            ),
            "next": (page.next_page_number() if page.has_next() else None),
            "results": list(queryset),
        }

        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, **kwargs):
        try:
            movie = kwargs["object"]
        except KeyError:
            raise Http404("Фильм не найден.")
        return movie
