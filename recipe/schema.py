import graphene
from graphql import GraphQLError
from graphene_django import DjangoObjectType
from .models import Ingredient, Recipe
from django.db.models import Q

class IngredientType(DjangoObjectType):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "details", "created_at")

class IngredientListType(graphene.ObjectType):
    total_count = graphene.Int()                      
    results = graphene.List(IngredientType)           

class RecipeType(DjangoObjectType):
    ingredient_count = graphene.Int()
    class Meta:
        model = Recipe
        fields = ("id", "title", "description", "ingredients", "created_at")

    def resolve_ingredient_count(self, info):
        return self.ingredients.count()

# create ingredient 
class CreateIngredient(graphene.Mutation):

    class Arguments:
        name = graphene.String(required=True)
        details = graphene.String(required=False)

    ingredient = graphene.Field(IngredientType)

    def mutate(self, info, name, details=None):
        user = info.context.user
        name = name.strip()
        details = (details or "").strip()
        if not name:
            raise GraphQLError("Ingredient name cannot be empty.")
        
        if Ingredient.objects.filter(name__iexact=name, created_by=user).exists():
            raise GraphQLError("You already created this ingredient.")

        ingredient = Ingredient.objects.create(name=name, details=details, created_by=user)
        return CreateIngredient(ingredient=ingredient)
    
#update ingredient

class UpdateIngredient(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        details = graphene.String()

    ingredient = graphene.Field(IngredientType)

    def mutate(self, info, id, name=None, details=None):
        try:
            ingredient = Ingredient.objects.get(pk=id)
        except Ingredient.DoesNotExist:
            raise Exception("Ingredient not found")

        if name is not None:
            ingredient.name = name
        if details is not None:
            ingredient.details = details

        ingredient.save()
        return UpdateIngredient(ingredient=ingredient)
    
#delete ingredient
class DeleteIngredient(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    message = graphene.String()

    def mutate(self, info, id):
        try:
            ingredient = Ingredient.objects.get(pk=id)
        except Ingredient.DoesNotExist:
            raise Exception("Ingredient not found")

        ingredient.delete()
        return DeleteIngredient(message="Ingredient deleted successfully")
    
#create recipe
class CreateRecipe(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String()
        ingredient_ids = graphene.List(graphene.ID)

    recipe = graphene.Field(RecipeType)

    def mutate(self, info, title, description=None, ingredient_ids=None):
        user = info.context.user
        title = title.strip()
        description = (description or "").strip()
        if not title:
            raise GraphQLError("Recipe title cannot be empty.")
        
        recipe = Recipe.objects.create(title=title, description=description, created_by=user)

        if ingredient_ids:
            ingredients = Ingredient.objects.filter(id__in=ingredient_ids, created_by=user)
            recipe.ingredients.set(ingredients)

        return CreateRecipe(recipe=recipe)
    
#add ingredient to recipe
class AddIngredientToRecipe(graphene.Mutation):
    class Arguments:
        recipe_id = graphene.ID(required=True)
        ingredient_ids = graphene.List(graphene.Int, required=True)

    recipe = graphene.Field(RecipeType)

    def mutate(self, info, recipe_id, ingredient_ids):
        user = info.context.user
        try:
            recipe = Recipe.objects.get(pk=recipe_id, created_by=user)
            ingredient = Ingredient.objects.filter(id__in=ingredient_ids, created_by=user)
        except Recipe.DoesNotExist:
            raise Exception("Recipe not found")
        except Ingredient.DoesNotExist:
            raise Exception("Ingredient not found")
        

        recipe.ingredients.add(*ingredient)
        return AddIngredientToRecipe(recipe=recipe)
    

#remove ingredient from recipe
class RemoveIngredientFromRecipe(graphene.Mutation):
    class Arguments:
        recipe_id = graphene.ID(required=True)
        ingredient_ids = graphene.List(graphene.Int, required=True)

    recipe = graphene.Field(RecipeType)

    def mutate(self, info, recipe_id, ingredient_ids):
        user = info.context.user
        try:
            recipe = Recipe.objects.get(pk=recipe_id, created_by=user)
            ingredient = Ingredient.objects.filter(id__in=ingredient_ids, created_by=user)
        except Recipe.DoesNotExist:
            raise Exception("Recipe not found")
        except Ingredient.DoesNotExist:
            raise Exception("Ingredient not found")
        
        recipe.ingredients.remove(*ingredient)
        return RemoveIngredientFromRecipe(recipe=recipe)
    
class Mutation(graphene.ObjectType):
    create_ingredient = CreateIngredient.Field()
    update_ingredient = UpdateIngredient.Field()
    delete_ingredient = DeleteIngredient.Field()
    create_recipe = CreateRecipe.Field()
    add_ingredient_to_recipe = AddIngredientToRecipe.Field()
    remove_ingredient_from_recipe = RemoveIngredientFromRecipe.Field()

class Query(graphene.ObjectType):
    
    all_ingredients = graphene.Field(IngredientListType, search=graphene.String(), page=graphene.Int(), limit=graphene.Int())

    def resolve_all_ingredients(self, info, search=None, page=None, limit=None):
        user = info.context.user
        qs = Ingredient.objects.filter(created_by=user).order_by("-created_at")
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(details__icontains=search)
            )
        total_count = qs.count()    
        paginated_qs = qs
        if page and limit:
            start = (page - 1) * limit
            end = start + limit
            paginated_qs = qs[start:end]

        return IngredientListType(total_count=total_count, results=paginated_qs)
    
    recipe = graphene.Field(RecipeType, id=graphene.ID(required=True))

    # get recipe by id
    def resolve_recipe(self, info, id):
        try:
            return Recipe.objects.get(pk=id)
        except Recipe.DoesNotExist:
            raise Exception("Recipe not found")
    


schema = graphene.Schema(query=Query,mutation=Mutation)

    
   
