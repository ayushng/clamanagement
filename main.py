import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os
import random
import string
import traceback
import asyncio
from typing import Optional
from datetime import datetime

# ================= CONFIG =================
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

GUILD_ID = 1382693923104751736
TICKET_CATEGORY_ID_CUSTOMER = 1413434358626521161
TICKET_CATEGORY_ID_MANAGEMENT = 1413434410530771076
SUPPORT_ROLE_ID = 1422464459791667311
MANAGEMENT_ROLE_ID = 1422464210037903371 # This is the only role that can use commands

# Quality Control Config
QC_CHANNEL_ID = 1412000892378546246  # Replace with your QC channel ID
QC_ROLE_ID = 1413130801599741962  # Replace with your Quality Control role ID

# Payment Proof Config
PAYMENT_PROOF_CHANNEL_ID = 1412004352079564871  # Replace with your payment proof channel ID

# Welcome Channel Config - PLEASE PROVIDE THE CORRECT CHANNEL ID
WELCOME_CHANNEL_ID = 1382694377578823783  # Replace with your welcome channel ID

TOP_BANNER_URL = "https://cdn.discordapp.com/attachments/1382693923536896083/1415628455105794108/Hello_THERE-5.png"
BOTTOM_BANNER_URL = "https://cdn.discordapp.com/attachments/1414155141107421294/1415647542867136566/Screenshot_2025-09-11_at_6.28.41_PM.png"
FOOTER_LOGO_URL = "https://cdn.discordapp.com/attachments/1414155141107421294/1415647206693666918/images-2-2.png"

# ================= ORDERING CONFIG =================
LIVERIES_CATEGORY_ID = 1416440222308237532  # Liveries orders category
UNIFORMS_CATEGORY_ID = 1416441953779847288  # Custom Uniforms orders category
ELS_CATEGORY_ID = 1416442140027785277  # ELS orders category
DISCORD_SERVICES_CATEGORY_ID = 1416442282705682565  # Discord Services orders category
CUSTOM_BOTS_CATEGORY_ID = 1416442383909916762  # Custom Bots orders category
MORE_CATEGORY_ID = 1416442652546699314  # More/Other orders category

DESIGNER_ROLE_ID = 1422464759315435564

# Infraction & Promotion Config
INFRACTION_CHANNEL_ID = 1420562684478357605  # Replace with your infraction channel ID
PROMOTION_CHANNEL_ID = 1420562790548111461  # Replace with your promotions/announcements channel ID
INFRACTION_BANNER_URL = "https://discord.com/channels/1382693923104751736/1414155141107421294/1425028583214153788"  # Red banner with "INFRACTION"
PROMOTION_BANNER_URL = "https://discord.com/channels/1382693923104751736/1414155141107421294/1425028583214153788"  # Green banner with "PROMOTION"

# You can use the same banner URLs or create new ones for orders
ORDER_BANNER_URL = "https://cdn.discordapp.com/attachments/1414155141107421294/1416779652797567126/Hello_THERE-2.png?ex=68c8165f&is=68c6c4df&hm=1f6eb3b8f157c6047fbcf58c4c1f49ca155c9bd48c86061f38eb6ba3bcd1be11"
ORDER_BOTTOM_URL = "https://cdn.discordapp.com/attachments/1414155141107421294/1416779652797567126/Hello_THERE-2.png?ex=68c8165f&is=68c6c4df&hm=1f6eb3b8f157c6047fbcf58c4c1f49ca155c9bd48c86061f38eb6ba3bcd1be11"

# ================= SETUP =================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)

# CONFIGURATION
WELCOME_BANNER_URL = "https://cdn.discordapp.com/attachments/1414155141107421294/1416779652797567126/Hello_THERE-2.png?ex=68c8165f&is=68c6c4df&hm=1f6eb3b8f157c6047fbcf58c4c1f49ca155c9bd48c86061f38eb6ba3bcd1be11"


# ================= PERMISSION CHECK FUNCTIONS =================
def has_management_role():
    """Decorator to check if user has the management role"""

    def predicate(ctx):
        management_role = ctx.guild.get_role(MANAGEMENT_ROLE_ID)
        if not management_role or management_role not in ctx.author.roles:
            return False
        return True

    return commands.check(predicate)


def check_management_role_interaction(interaction: discord.Interaction) -> bool:
    """Check if user has management role for slash commands"""
    management_role = interaction.guild.get_role(MANAGEMENT_ROLE_ID)
    return management_role and management_role in interaction.user.roles


# ================= ERROR HANDLING DECORATORS =================
def handle_interaction_errors(func):
    """Decorator to handle interaction errors gracefully"""

    async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
        try:
            return await func(self, interaction, *args, **kwargs)
        except discord.NotFound:
            logger.error(f"Discord object not found in {func.__name__}: {traceback.format_exc()}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ Something went wrong. This may be an old message.",
                                                            ephemeral=True)
                else:
                    await interaction.followup.send("❌ Something went wrong. This may be an old message.",
                                                    ephemeral=True)
            except:
                pass
        except discord.Forbidden:
            logger.error(f"Discord permissions error in {func.__name__}: {traceback.format_exc()}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ I don't have the necessary permissions to perform this action.", ephemeral=True)
                else:
                    await interaction.followup.send("❌ I don't have the necessary permissions to perform this action.",
                                                    ephemeral=True)
            except:
                pass
        except discord.HTTPException as e:
            logger.error(f"Discord HTTP error in {func.__name__}: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ Discord is having issues. Please try again later.",
                                                            ephemeral=True)
                else:
                    await interaction.followup.send("❌ Discord is having issues. Please try again later.",
                                                    ephemeral=True)
            except:
                pass
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}\n{traceback.format_exc()}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ An unexpected error occurred. Please try again.",
                                                            ephemeral=True)
                else:
                    await interaction.followup.send("❌ An unexpected error occurred. Please try again.", ephemeral=True)
            except:
                pass

    return wrapper


# ================= HELPER FUNCTIONS =================
def generate_order_number() -> str:
    """Generate a unique order number"""
    return ''.join(random.choices(string.digits, k=3))


def check_existing_orders(guild: discord.Guild, user: discord.Member) -> Optional[discord.TextChannel]:
    """Check if user has any existing order channels and return the first one found"""
    try:
        order_categories = [
            LIVERIES_CATEGORY_ID, UNIFORMS_CATEGORY_ID, ELS_CATEGORY_ID,
            DISCORD_SERVICES_CATEGORY_ID, CUSTOM_BOTS_CATEGORY_ID, MORE_CATEGORY_ID
        ]

        for category_id in order_categories:
            category = guild.get_channel(category_id)
            if category and isinstance(category, discord.CategoryChannel):
                for channel in category.channels:
                    if isinstance(channel, discord.TextChannel):
                        # Check if the user has permissions to view this channel (meaning it's their order)
                        overwrites = channel.overwrites_for(user)
                        if overwrites.view_channel is True:
                            return channel
        return None
    except Exception as e:
        logger.error(f"Error checking existing orders: {e}")
        return None


def find_order_channel_by_customer(guild: discord.Guild, customer_username: str) -> tuple[
    Optional[discord.TextChannel], Optional[discord.Member]]:
    """Find order channel and customer by username"""
    try:
        order_categories = [
            LIVERIES_CATEGORY_ID, UNIFORMS_CATEGORY_ID, ELS_CATEGORY_ID,
            DISCORD_SERVICES_CATEGORY_ID, CUSTOM_BOTS_CATEGORY_ID, MORE_CATEGORY_ID
        ]

        for category_id in order_categories:
            category = guild.get_channel(category_id)
            if category and isinstance(category, discord.CategoryChannel):
                for channel in category.channels:
                    if isinstance(channel, discord.TextChannel):
                        # Check if the customer username is in channel name or topic
                        if customer_username.lower() in channel.name.lower():
                            # Try to extract customer from channel overwrites
                            for user, overwrites in channel.overwrites.items():
                                if isinstance(user, discord.Member) and overwrites.view_channel is True:
                                    if not any(
                                            role.id in [DESIGNER_ROLE_ID, SUPPORT_ROLE_ID, MANAGEMENT_ROLE_ID] for
                                            role in user.roles):
                                        return channel, user
                            return channel, None

                        # Also check channel topic
                        if channel.topic and customer_username.lower() in channel.topic.lower():
                            for user, overwrites in channel.overwrites.items():
                                if isinstance(user, discord.Member) and overwrites.view_channel is True:
                                    if not any(
                                            role.id in [DESIGNER_ROLE_ID, SUPPORT_ROLE_ID, MANAGEMENT_ROLE_ID] for role
                                            in user.roles):
                                        return channel, user
                            return channel, None

        return None, None
    except Exception as e:
        logger.error(f"Error finding order channel: {e}")
        return None, None


def get_customer_from_username(guild: discord.Guild, username: str) -> Optional[discord.Member]:
    """Find customer by username or display name"""
    try:
        # Try exact match first
        for member in guild.members:
            if member.name.lower() == username.lower() or member.display_name.lower() == username.lower():
                return member

        # Try partial match
        for member in guild.members:
            if username.lower() in member.name.lower() or username.lower() in member.display_name.lower():
                return member

        return None
    except Exception as e:
        logger.error(f"Error finding customer by username: {e}")
        return None


# ================= QUALITY CONTROL VIEW =================
class QCApprovalView(discord.ui.View):
    def __init__(self, customer_username: str, product_type: str, notes: str,
                 designer: discord.Member, order_channel: discord.TextChannel = None):
        super().__init__(timeout=None)
        self.customer_username = customer_username
        self.product_type = product_type
        self.notes = notes
        self.designer = designer
        self.order_channel = order_channel

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green, custom_id="qc_approve")
    @handle_interaction_errors
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        qc_role = interaction.guild.get_role(QC_ROLE_ID)
        management_role = interaction.guild.get_role(MANAGEMENT_ROLE_ID)

        # Allow both QC role and management role to approve
        if not ((qc_role and qc_role in interaction.user.roles) or (
                management_role and management_role in interaction.user.roles)):
            await interaction.response.send_message("❌ You don't have permission to approve products.", ephemeral=True)
            return

        # Send approval message to QC channel
        embed = discord.Embed(
            title="✅ Product Approved!",
            description=f"Product for **{self.customer_username}** has been approved for release!",
            color=0x00ff00
        )
        embed.add_field(name="Customer", value=self.customer_username, inline=True)
        embed.add_field(name="Product Type", value=self.product_type, inline=True)
        embed.add_field(name="Designer", value=self.designer.mention if self.designer else "Unknown", inline=True)
        embed.add_field(name="Approved By", value=interaction.user.mention, inline=False)
        embed.set_footer(text="This product is now ready for delivery!", icon_url=FOOTER_LOGO_URL)

        await interaction.response.send_message(embed=embed)

        # Send confirmation to order channel if it exists
        if self.order_channel:
            try:
                qc_confirmation = discord.Embed(
                    title="✅ Quality Control Approved",
                    description=f"Your design has been approved by Quality Control!",
                    color=0x00ff00
                )
                qc_confirmation.add_field(name="Approved By", value=interaction.user.mention, inline=True)
                qc_confirmation.add_field(name="Status", value="✅ QC Approved", inline=True)
                qc_confirmation.set_footer(text="Your order is one step closer to completion!",
                                           icon_url=FOOTER_LOGO_URL)

                await self.order_channel.send(embed=qc_confirmation)
            except Exception as e:
                logger.error(f"Error sending QC confirmation to order channel: {e}")

        # Disable all buttons
        for item in self.children:
            item.disabled = True
        await interaction.edit_original_response(view=self)

    @discord.ui.button(label="Denied", style=discord.ButtonStyle.red, custom_id="qc_deny")
    @handle_interaction_errors
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        qc_role = interaction.guild.get_role(QC_ROLE_ID)
        management_role = interaction.guild.get_role(MANAGEMENT_ROLE_ID)

        # Allow both QC role and management role to deny
        if not ((qc_role and qc_role in interaction.user.roles) or (
                management_role and management_role in interaction.user.roles)):
            await interaction.response.send_message("❌ You don't have permission to deny products.", ephemeral=True)
            return

        # Create modal for denial reason
        modal = QCDenialModal(self.customer_username, self.product_type, self.designer, self.order_channel)
        await interaction.response.send_modal(modal)

        # Disable all buttons
        for item in self.children:
            item.disabled = True
        await interaction.edit_original_response(view=self)


class QCDenialModal(discord.ui.Modal, title="Quality Control - Denial Reason"):
    def __init__(self, customer_username: str, product_type: str, designer: discord.Member,
                 order_channel: discord.TextChannel = None):
        super().__init__()
        self.customer_username = customer_username
        self.product_type = product_type
        self.designer = designer
        self.order_channel = order_channel

    reason = discord.ui.TextInput(
        label="Reason for Denial",
        placeholder="Please explain why this product was denied...",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Send denial message to QC channel
            embed = discord.Embed(
                title="❌ Product Denied",
                description=f"Product for **{self.customer_username}** has been denied.",
                color=0xff0000
            )
            embed.add_field(name="Customer", value=self.customer_username, inline=True)
            embed.add_field(name="Product Type", value=self.product_type, inline=True)
            embed.add_field(name="Designer", value=self.designer.mention if self.designer else "Unknown", inline=True)
            embed.add_field(name="Denied By", value=interaction.user.mention, inline=False)
            embed.add_field(name="Reason", value=self.reason.value, inline=False)
            embed.set_footer(text="Please make the necessary changes and resubmit.", icon_url=FOOTER_LOGO_URL)

            await interaction.response.send_message(embed=embed)

            # Send denial notice to order channel if it exists
            if self.order_channel:
                try:
                    denial_notice = discord.Embed(
                        title="❌ Quality Control - Revisions Required",
                        description=f"Your design requires revisions before approval.",
                        color=0xff0000
                    )
                    denial_notice.add_field(name="Denied By", value=interaction.user.mention, inline=True)
                    denial_notice.add_field(name="Reason for Denial", value=self.reason.value, inline=False)
                    denial_notice.add_field(name="Next Steps",
                                            value="The designer will make the necessary changes and resubmit for QC review.",
                                            inline=False)
                    denial_notice.set_footer(text="Don't worry - we'll get this perfect for you!",
                                             icon_url=FOOTER_LOGO_URL)

                    await self.order_channel.send(embed=denial_notice)
                except Exception as e:
                    logger.error(f"Error sending QC denial to order channel: {e}")

        except Exception as e:
            logger.error(f"Error in QC denial modal: {e}")
            await interaction.response.send_message("❌ An error occurred while processing the denial.", ephemeral=True)


# ================= PAYMENT VERIFICATION VIEW =================
class PaymentVerificationView(discord.ui.View):
    def __init__(self, customer_username: str, customer: discord.Member, order_channel: discord.TextChannel):
        super().__init__(timeout=None)
        self.customer_username = customer_username
        self.customer = customer
        self.order_channel = order_channel

    @discord.ui.button(label="✅ Verify Payment", style=discord.ButtonStyle.green, custom_id="payment_verify")
    @handle_interaction_errors
    async def verify_payment(self, interaction: discord.Interaction, button: discord.ui.Button):
        management_role = interaction.guild.get_role(MANAGEMENT_ROLE_ID)
        if not management_role or management_role not in interaction.user.roles:
            await interaction.response.send_message("❌ Only management can verify payments.", ephemeral=True)
            return

        # Send verification message
        embed = discord.Embed(
            title="✅ Payment Verified!",
            description=f"Payment for **{self.customer_username}** has been verified and confirmed!",
            color=0x00ff00
        )
        embed.add_field(name="Customer",
                        value=f"{self.customer.display_name if self.customer else self.customer_username}",
                        inline=True)
        embed.add_field(name="Verified By", value=interaction.user.mention, inline=True)
        embed.add_field(name="Order Channel", value=self.order_channel.mention if self.order_channel else "N/A",
                        inline=True)
        embed.set_footer(text="Payment confirmed - Order can now be completed!", icon_url=FOOTER_LOGO_URL)

        await interaction.response.send_message(embed=embed)

        # Send confirmation to order channel
        if self.order_channel:
            try:
                payment_confirmed = discord.Embed(
                    title="✅ Payment Confirmed",
                    description=f"Your payment has been verified!",
                    color=0x00ff00
                )
                payment_confirmed.add_field(name="Verified By", value=interaction.user.mention, inline=True)
                payment_confirmed.add_field(name="Status", value="✅ Payment Confirmed", inline=True)
                payment_confirmed.set_footer(text="Your order is now ready for completion!", icon_url=FOOTER_LOGO_URL)

                await self.order_channel.send(embed=payment_confirmed)
            except Exception as e:
                logger.error(f"Error sending payment confirmation to order channel: {e}")

        # Disable all buttons
        for item in self.children:
            item.disabled = True
        await interaction.edit_original_response(view=self)

    @discord.ui.button(label="❌ Reject Payment", style=discord.ButtonStyle.red, custom_id="payment_reject")
    @handle_interaction_errors
    async def reject_payment(self, interaction: discord.Interaction, button: discord.ui.Button):
        management_role = interaction.guild.get_role(MANAGEMENT_ROLE_ID)
        if not management_role or management_role not in interaction.user.roles:
            await interaction.response.send_message("❌ Only management can reject payments.", ephemeral=True)
            return

        # Create modal for rejection reason
        modal = PaymentRejectionModal(self.customer_username, self.customer, self.order_channel)
        await interaction.response.send_modal(modal)

        # Disable all buttons
        for item in self.children:
            item.disabled = True
        await interaction.edit_original_response(view=self)


class PaymentRejectionModal(discord.ui.Modal, title="Payment Rejection - Reason"):
    def __init__(self, customer_username: str, customer: discord.Member, order_channel: discord.TextChannel):
        super().__init__()
        self.customer_username = customer_username
        self.customer = customer
        self.order_channel = order_channel

    reason = discord.ui.TextInput(
        label="Reason for Rejection",
        placeholder="Please explain why this payment was rejected...",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Send rejection message
            embed = discord.Embed(
                title="❌ Payment Rejected",
                description=f"Payment proof for **{self.customer_username}** has been rejected.",
                color=0xff0000
            )
            embed.add_field(name="Customer",
                            value=f"{self.customer.display_name if self.customer else self.customer_username}",
                            inline=True)
            embed.add_field(name="Rejected By", value=interaction.user.mention, inline=True)
            embed.add_field(name="Reason", value=self.reason.value, inline=False)
            embed.set_footer(text="Please resubmit with correct payment proof.", icon_url=FOOTER_LOGO_URL)

            await interaction.response.send_message(embed=embed)

            # Send rejection notice to order channel
            if self.order_channel:
                try:
                    rejection_notice = discord.Embed(
                        title="❌ Payment Proof Rejected",
                        description=f"Your payment proof has been rejected.",
                        color=0xff0000
                    )
                    rejection_notice.add_field(name="Rejected By", value=interaction.user.mention, inline=True)
                    rejection_notice.add_field(name="Reason", value=self.reason.value, inline=False)
                    rejection_notice.add_field(name="Next Steps",
                                               value="Please submit correct payment proof using `/payment-proof` command.",
                                               inline=False)
                    rejection_notice.set_footer(text="We're here to help if you need assistance!",
                                                icon_url=FOOTER_LOGO_URL)

                    await self.order_channel.send(embed=rejection_notice)
                except Exception as e:
                    logger.error(f"Error sending payment rejection to order channel: {e}")

        except Exception as e:
            logger.error(f"Error in payment rejection modal: {e}")
            await interaction.response.send_message("❌ An error occurred while processing the rejection.",
                                                    ephemeral=True)


# ================= TICKET ACTION VIEW =================
class TicketActionView(discord.ui.View):
    def __init__(self, member: discord.Member = None, role_id: int = None):
        super().__init__(timeout=None)
        self.member = member
        self.role_id = role_id

    @discord.ui.button(label="🎫 Claim Ticket", style=discord.ButtonStyle.green, custom_id="ticket_claim")
    @handle_interaction_errors
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.role_id:
            await interaction.response.send_message("❌ Ticket configuration error.", ephemeral=True)
            return

        role = interaction.guild.get_role(self.role_id)
        if not role or role not in interaction.user.roles:
            await interaction.response.send_message("❌ You are not authorized to claim this ticket.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🎫 Ticket Claimed",
            description=f"{interaction.user.mention} has claimed this ticket!",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed)

        button.disabled = True
        button.label = f"Claimed by {interaction.user.display_name}"
        await interaction.edit_original_response(view=self)

    @discord.ui.button(label="🗑️ Close Ticket", style=discord.ButtonStyle.red, custom_id="ticket_close")
    @handle_interaction_errors
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.role_id:
            await interaction.response.send_message("❌ Ticket configuration error.", ephemeral=True)
            return

        role = interaction.guild.get_role(self.role_id)
        authorized = (role and role in interaction.user.roles) or (self.member and interaction.user == self.member)

        if not authorized:
            await interaction.response.send_message("❌ You are not authorized to close this ticket.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🗑️ Closing Ticket",
            description="This ticket will be deleted in 5 seconds...",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed)

        # Wait 5 seconds then delete
        try:
            await asyncio.sleep(5)
            await interaction.followup.send("Ticket closed. Goodbye! 👋")
            await asyncio.sleep(1)
            await interaction.channel.delete()
        except discord.NotFound:
            logger.info("Channel already deleted")
        except Exception as e:
            logger.error(f"Error deleting ticket channel: {e}")


# ================= TICKET PANEL VIEW =================
class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_ticket_channel(self, interaction: discord.Interaction, category_name: str, category_id: int,
                                    role_id: int):
        try:
            guild = bot.get_guild(GUILD_ID)
            if not guild:
                await interaction.response.send_message("❌ Could not find the guild.", ephemeral=True)
                return

            category = guild.get_channel(category_id)
            if not category or not isinstance(category, discord.CategoryChannel):
                await interaction.response.send_message("❌ Could not find the ticket category.", ephemeral=True)
                return

            member = interaction.user
            channel_name = f"{category_name.lower().replace(' ', '-')}-{member.display_name}".replace(' ', '-')

            # Check for existing tickets
            for channel in guild.channels:
                if channel.name == channel_name and isinstance(channel, discord.TextChannel):
                    await interaction.response.send_message(f"❌ You already have a ticket: {channel.mention}",
                                                            ephemeral=True)
                    return

            # Set up permissions
            support_role = guild.get_role(role_id)
            if not support_role:
                await interaction.response.send_message("❌ Support role not found.", ephemeral=True)
                return

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
                support_role: discord.PermissionOverwrite(view_channel=True, send_messages=True,
                                                          read_message_history=True, manage_messages=True)
            }

            ticket_channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites,
                topic=f"{category_name} ticket for {member.display_name}"
            )

            # Welcome embed
            embed = discord.Embed(
                title=f"🎫 {category_name} Ticket",
                description=f"Hello {member.mention}! 👋\n\nYour ticket has been created successfully. Please describe your issue and a team member will assist you shortly.\n\n**Ticket ID:** `{ticket_channel.id}`",
                color=0x2B2D31
            )
            embed.set_footer(text="Use the buttons below to manage this ticket", icon_url=FOOTER_LOGO_URL)

            await ticket_channel.send(f"{member.mention}", embed=embed, view=TicketActionView(member, role_id))
            await interaction.response.send_message(f"✅ Your ticket has been created: {ticket_channel.mention}",
                                                    ephemeral=True)

        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to create channels.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error creating ticket channel: {e}")
            await interaction.response.send_message(f"❌ An error occurred while creating your ticket.", ephemeral=True)

    @discord.ui.select(
        placeholder="🎫 Select a support category to create your ticket...",
        min_values=1,
        max_values=1,
        custom_id="ticket_dropdown",
        options=[
            discord.SelectOption(
                label="Customer Support",
                description="Order issues, product support, staff reports & general assistance",
                value="customer",
                emoji="🛠️"
            ),
            discord.SelectOption(
                label="Management",
                description="Partnerships, applications, perk claims & moderation appeals",
                value="management",
                emoji="⚙️"
            )
        ]
    )
    @handle_interaction_errors
    async def ticket_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        category_mapping = {
            "customer": ("Customer Support", TICKET_CATEGORY_ID_CUSTOMER, SUPPORT_ROLE_ID),
            "management": ("Management", TICKET_CATEGORY_ID_MANAGEMENT, MANAGEMENT_ROLE_ID)
        }

        selected_value = select.values[0]
        category_name, category_id, role_id = category_mapping[selected_value]

        await self.create_ticket_channel(interaction, category_name, category_id, role_id)


# ================= ORDER ACTION VIEW =================
class OrderActionView(discord.ui.View):
    def __init__(self, member: discord.Member = None, order_type: str = None, order_number: str = None):
        super().__init__(timeout=None)
        self.member = member
        self.order_type = order_type
        self.order_number = order_number

    @discord.ui.button(label="📋 Terms & Conditions", style=discord.ButtonStyle.secondary, custom_id="tc_button", row=0)
    @handle_interaction_errors
    async def terms_conditions(self, interaction: discord.Interaction, button: discord.ui.Button):
        tc_embed = discord.Embed(
            title="📋 Terms & Conditions - CLA Designs",
            description="""
**By using our services, you agree to the following terms and conditions:**

🔗 **Full Terms & Conditions Document:**
[Click here to read our complete T&C](https://docs.google.com/document/d/1vJ4W8-QmtL5nx8mH1bgZtIn7iPDD6uwBuaNnb3J3_8k/edit?pli=1&tab=t.0)

⚠️ **Important Notice:**
You **MUST** agree to our Terms & Conditions to use our services. By placing an order or using any of our design services, you acknowledge that you have read, understood, and agree to be bound by these terms.

**Key Points:**
- All sales are final unless otherwise specified
- Payment must be completed before work begins
- Unlimited revisions are included within reason
- We reserve the right to refuse service
- All designs remain property of CLA Designs until payment
- No refunds for completed work unless agreed upon

**By continuing with your order, you confirm that you agree to these terms.**
            """,
            color=0x2B2D31
        )
        tc_embed.set_footer(text="Please read our full Terms & Conditions document", icon_url=FOOTER_LOGO_URL)

        await interaction.response.send_message(embed=tc_embed, ephemeral=True)

    @discord.ui.button(label="🎨 Claim Order", style=discord.ButtonStyle.green, custom_id="order_claim", row=1)
    @handle_interaction_errors
    async def claim_order(self, interaction: discord.Interaction, button: discord.ui.Button):
        designer_role = interaction.guild.get_role(DESIGNER_ROLE_ID)
        if not designer_role or designer_role not in interaction.user.roles:
            await interaction.response.send_message("❌ You must be a designer to claim orders.", ephemeral=True)
            return

        # Update channel name to include designer and green emoji
        try:
            service_type = self.order_type.lower().replace(' ', '-')
            new_channel_name = f"🟢-{service_type}-{self.order_number}-{interaction.user.display_name}".replace(' ',
                                                                                                               '-').replace(
                ':', '')
            await interaction.channel.edit(name=new_channel_name)
        except Exception as e:
            logger.error(f"Error updating channel name: {e}")

        embed = discord.Embed(
            title="🎨 Order Claimed!",
            description=f"**Designer:** {interaction.user.mention}\n**Client:** {self.member.mention if self.member else 'Unknown'}\n**Service:** {self.order_type}\n**Order #:** {self.order_number}",
            color=0x00ff88
        )
        embed.add_field(name="Next Steps", value="The designer will discuss details and pricing with you shortly!",
                        inline=False)
        embed.add_field(name="⚠️ Important",
                        value="By proceeding with this order, you agree to our [Terms & Conditions](https://docs.google.com/document/d/1vJ4W8-QmtL5nx8mH1bgZtIn7iPDD6uwBuaNnb3J3_8k/edit?pli=1&tab=t.0)",
                        inline=False)

        await interaction.response.send_message(embed=embed)

        button.disabled = True
        button.label = f"Claimed by {interaction.user.display_name}"
        button.style = discord.ButtonStyle.gray
        await interaction.edit_original_response(view=self)

    @discord.ui.button(label="✅ Mark Complete", style=discord.ButtonStyle.blurple, custom_id="order_complete", row=1)
    @handle_interaction_errors
    async def complete_order(self, interaction: discord.Interaction, button: discord.ui.Button):
        designer_role = interaction.guild.get_role(DESIGNER_ROLE_ID)
        management_role = interaction.guild.get_role(MANAGEMENT_ROLE_ID)

        # Only designers, management, or the client can mark complete
        authorized = (designer_role and designer_role in interaction.user.roles) or \
                     (management_role and management_role in interaction.user.roles) or \
                     (self.member and interaction.user == self.member)

        if not authorized:
            await interaction.response.send_message(
                "❌ Only the designer, management, or client can mark this complete.", ephemeral=True)
            return

        embed = discord.Embed(
            title="✅ Order Completed!",
            description=f"Order #{self.order_number} has been marked as complete by {interaction.user.mention}",
            color=0x00ff00
        )
        embed.add_field(name="Thank you!", value="Hope you're happy with your design! 🎨", inline=False)

        await interaction.response.send_message(embed=embed)

        # Disable all buttons
        for item in self.children:
            item.disabled = True
        await interaction.edit_original_response(view=self)

    @discord.ui.button(label="🗑️ Close Order", style=discord.ButtonStyle.red, custom_id="order_close", row=1)
    @handle_interaction_errors
    async def close_order(self, interaction: discord.Interaction, button: discord.ui.Button):
        @discord.ui.button(label="🗑️ Close Order", style=discord.ButtonStyle.red, custom_id="order_close", row=1)
        @handle_interaction_errors
        async def close_order(self, interaction: discord.Interaction, button: discord.ui.Button):
            # Allow both designers and management to close orders
            designer_role = interaction.guild.get_role(DESIGNER_ROLE_ID)
            management_role = interaction.guild.get_role(MANAGEMENT_ROLE_ID)

            authorized = (designer_role and designer_role in interaction.user.roles) or \
                         (management_role and management_role in interaction.user.roles)

            if not authorized:
                await interaction.response.send_message("❌ Only designers and management can close orders.",
                                                        ephemeral=True)
                return

        embed = discord.Embed(
            title="🗑️ Closing Order",
            description="This order channel will be deleted in 10 seconds...",
            color=0xff4444
        )
        await interaction.response.send_message(embed=embed)

        try:
            await asyncio.sleep(10)
            await interaction.followup.send("Order closed! Thank you for using our services! 👋")
            await asyncio.sleep(2)
            await interaction.channel.delete()
        except discord.NotFound:
            logger.info("Channel already deleted")
        except Exception as e:
            logger.error(f"Error deleting order channel: {e}")
# ================= ORDERING PANEL VIEW =================
class OrderingPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_order_channel(self, interaction: discord.Interaction, service_type: str, emoji: str,
                                   category_id: int):
        try:
            guild = bot.get_guild(GUILD_ID)
            if not guild:
                await interaction.response.send_message("❌ Could not find the guild.", ephemeral=True)
                return

            member = interaction.user

            # Check if user has any existing orders
            existing_order = check_existing_orders(guild, member)
            if existing_order:
                await interaction.response.send_message(
                    f"❌ **You already have an active order!**\n\nYou can only have **1 order at a time** to prevent spam.\n\n**Your existing order:** {existing_order.mention}\n\nPlease complete or close your current order before placing a new one.",
                    ephemeral=True
                )
                return

            category = guild.get_channel(category_id)
            if not category or not isinstance(category, discord.CategoryChannel):
                await interaction.response.send_message(f"❌ Could not find the {service_type} category.",
                                                        ephemeral=True)
                return

            # Generate unique order number
            order_number = generate_order_number()
            channel_name = f"{service_type.lower().replace(' ', '-')}-{order_number}-{member.display_name}".replace(' ',
                                                                                                                    '-').replace(
                ':', '')

            # Set up permissions
            designer_role = guild.get_role(DESIGNER_ROLE_ID)
            if not designer_role:
                await interaction.response.send_message("❌ Designer role not found.", ephemeral=True)
                return

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
                designer_role: discord.PermissionOverwrite(view_channel=True, send_messages=True,
                                                           read_message_history=True, manage_messages=True)
            }

            order_channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites,
                topic=f"{service_type} order #{order_number} for {member.display_name}"
            )

            # Welcome embed with ER:LC styling
            embed = discord.Embed(
                title=f"{emoji} {service_type} Order",
                description=f"""
**Welcome {member.mention}!** 🚨

Thank you for choosing our {service_type.lower()} service! 

**What happens next:**
• A designer will claim your order shortly
• They'll discuss your requirements and pricing  
• Payment is handled through Robux
• We'll create your amazing design!

**Order Details:**
• **Client:** {member.mention}
• **Service:** {service_type}
• **Order Number:** `#{order_number}`
• **Order ID:** `{order_channel.id}`
• **Status:** 🟡 Waiting for Designer

**Please share:**
• What exactly you need designed
• Any reference images or inspiration  
• Your budget range in Robux
• Timeline/deadline requirements

⚠️ **Note:** You can only have **1 active order at a time**. Complete this order before placing another.
                """,
                color=0x2B2D31
            )

            embed.add_field(
                name="📋 Service Info - " + service_type,
                value=self.get_service_description(service_type),
                inline=False
            )

            embed.set_footer(text="ER:LC Design Services • Professional Quality Guaranteed", icon_url=FOOTER_LOGO_URL)

            await order_channel.send(f"🚨 {member.mention} • New {service_type} Order #{order_number}!", embed=embed,
                                     view=OrderActionView(member, service_type, order_number))
            await interaction.response.send_message(
                f"✅ Your {service_type.lower()} order has been created: {order_channel.mention}\n\n📋 **Order Number:** `#{order_number}`\n⚠️ **Remember:** You can only have 1 active order at a time!",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to create channels.", ephemeral=True)
        except Exception as e:
            logger.error(f"Error creating order channel: {e}")
            await interaction.response.send_message(f"❌ An error occurred while creating your order.", ephemeral=True)

    def get_service_description(self, service_type: str) -> str:
        descriptions = {
            "Liveries": "Custom vehicle skins and designs for your ER:LC fleet. Professional, realistic liveries for police, fire, EMS, and civilian vehicles.",
            "Custom Uniforms": "Custom uniform designs for your department or organization. Includes badges, patches, and complete uniform sets.",
            "ELS": "Emergency Lighting System configurations tailored to your vehicles. Professional setups for maximum realism.",
            "Discord Services": "Complete Discord server setup, bots, custom emojis, and server management tools for your ER:LC community.",
            "Custom Bots": "Fully customized Discord bots built specifically for your server's needs. Advanced features and functionality included.",
            "More": "Additional services or custom requests. Let us know what you need and we'll work with you to create something amazing!"
        }
        return descriptions.get(service_type,
                                "Professional design service for Emergency Response: Liberty County community.")

    @discord.ui.select(
        placeholder="🎨 Choose your service type...",
        min_values=1,
        max_values=1,
        custom_id="order_dropdown",
        options=[
            discord.SelectOption(
                label="Vehicle Liveries",
                description="Professional police, fire, EMS & civilian vehicle designs",
                value="liveries",
                emoji="🚗"
            ),
            discord.SelectOption(
                label="Custom Uniforms",
                description="Department uniforms, badges, patches & complete uniform sets",
                value="uniforms",
                emoji="👮"
            ),
            discord.SelectOption(
                label="ELS Configurations",
                description="Emergency lighting systems for maximum realism & immersion",
                value="els",
                emoji="🚨"
            ),
            discord.SelectOption(
                label="Discord Services",
                description="Server setup, bots, emojis & complete community management",
                value="discord",
                emoji="🤖"
            ),
            discord.SelectOption(
                label="Custom Bots",
                description="Fully personalized Discord bots with advanced features",
                value="bots",
                emoji="⚙️"
            ),
            discord.SelectOption(
                label="Additional Services",
                description="Special requests, custom projects & unique design needs",
                value="more",
                emoji="➕"
            )
        ]
    )
    @handle_interaction_errors
    async def order_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        service_mapping = {
            "liveries": ("Liveries", "🚗", LIVERIES_CATEGORY_ID),
            "uniforms": ("Custom Uniforms", "👮", UNIFORMS_CATEGORY_ID),
            "els": ("ELS", "🚨", ELS_CATEGORY_ID),
            "discord": ("Discord Services", "🤖", DISCORD_SERVICES_CATEGORY_ID),
            "bots": ("Custom Bots", "⚙️", CUSTOM_BOTS_CATEGORY_ID),
            "more": ("More", "➕", MORE_CATEGORY_ID)
        }

        selected_value = select.values[0]
        service_type, emoji, category_id = service_mapping[selected_value]

        await self.create_order_channel(interaction, service_type, emoji, category_id)


# ================= RECEIPT MODAL =================
class ReceiptModal(discord.ui.Modal, title="Generate Receipt - CLA Designs"):
    def __init__(self):
        super().__init__()

    order_id = discord.ui.TextInput(
        label="Order ID",
        placeholder="Enter unique order ID...",
        max_length=50,
        required=True
    )

    customer_username = discord.ui.TextInput(
        label="Customer Roblox Username",
        placeholder="Enter customer's Roblox username...",
        max_length=100,
        required=True
    )

    item_service = discord.ui.TextInput(
        label="Item / Service",
        placeholder="e.g., Custom Livery Design, Discord Bot Setup...",
        max_length=200,
        required=True
    )

    description = discord.ui.TextInput(
        label="Description",
        placeholder="Short description of the work completed...",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=True
    )

    total_amount = discord.ui.TextInput(
        label="Total Amount (Robux)",
        placeholder="Enter total amount in Robux (numbers only)...",
        max_length=20,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Validate amount is numeric
            try:
                amount = int(self.total_amount.value.replace(',', ''))
                formatted_amount = f"{amount:,}"
            except ValueError:
                await interaction.response.send_message("❌ Please enter a valid numeric amount for Robux.",
                                                        ephemeral=True)
                return

            # Get current date
            current_date = datetime.now().strftime("%B %d, %Y")

            # Create receipt embed
            receipt_embed = discord.Embed(
                title="🧾 CLA Designs – Receipt",
                color=0x2B2D31
            )

            receipt_content = f"""
📅 **Date:** {current_date}
🆔 **Order ID:** {self.order_id.value}
👤 **Customer Username:** {self.customer_username.value}
---------------------------------------------
📦 **Purchase Details**
**Item / Service:** {self.item_service.value}
**Description:** {self.description.value}
**Quantity:** 1
**Price per Unit:** R${formatted_amount}
**Total:** R${formatted_amount}

💸 **Total Paid:** R${formatted_amount}
---------------------------------------------
💼 **Payment Method**
Robux (R$) via Shirt
✔️ Payment Confirmed
---------------------------------------------
🛠️ **Designer:** {interaction.user.display_name}
🛑 **Note:**
All sales are final. No refunds unless otherwise agreed.
Designs are custom-made for ER:LC and delivered as per agreement.
---------------------------------------------
🔗 **Join our group:** https://www.roblox.com/communities/900583131/CLA-Designs#!/about

**Thank you for choosing CLA Designs! 🎨**
            """

            receipt_embed.description = receipt_content
            receipt_embed.set_footer(text="CLA Designs • Professional ER:LC Services", icon_url=FOOTER_LOGO_URL)
            receipt_embed.timestamp = discord.utils.utcnow()

            # Send receipt in the current channel
            await interaction.response.send_message(embed=receipt_embed)

        except Exception as e:
            logger.error(f"Error generating receipt: {e}")
            await interaction.response.send_message("❌ An error occurred while generating the receipt.", ephemeral=True)


# ================= SIMPLE WELCOME SYSTEM =================
@bot.event
async def on_member_join(member: discord.Member):
    """Send welcome message when a new member joins"""
    try:
        # Use the configured welcome channel ID if set
        welcome_channel = None
        if WELCOME_CHANNEL_ID:
            welcome_channel = member.guild.get_channel(WELCOME_CHANNEL_ID)

        # Fallback to finding welcome channel by name
        if not welcome_channel:
            welcome_names = ['welcome', 'general', 'announcements', 'directory-board']
            for channel in member.guild.text_channels:
                if any(name in channel.name.lower() for name in welcome_names):
                    welcome_channel = channel
                    break

        if not welcome_channel:
            return

        # Get random country flag
        flags = ["🇺🇸", "🇬🇧", "🇨🇦", "🇦🇺", "🇩🇪", "🇫🇷", "🇮🇹", "🇪🇸", "🇳🇱", "🇸🇪"]
        user_flag = random.choice(flags)

        # Send banner first
        if WELCOME_BANNER_URL:
            banner_embed = discord.Embed(color=0x2B2D31)
            banner_embed.set_image(url=WELCOME_BANNER_URL)
            await welcome_channel.send(embed=banner_embed)

        # Then send welcome text below
        embed = discord.Embed(
            title="Welcome to CLA Designs!",
            description="Hope you enjoy your stay, feel free to order any time.",
            color=0x2B2D31
        )
        embed.add_field(
            name="Get Started",
            value="Please check out the Reaction Roles to keep yourself updated and engage with the community!",
            inline=False
        )
        embed.set_footer(text="CLA Designs • Professional ER:LC Design Services")
        embed.timestamp = discord.utils.utcnow()

        # Send welcome message
        welcome_msg = f"Hello {member.mention} 😎 {user_flag}, welcome to CLA Designs."
        await welcome_channel.send(welcome_msg, embed=embed)

    except Exception as e:
        logger.error(f"Error in welcome system: {e}")


# ================= COMMAND ERROR HANDLERS =================
@bot.event
async def on_command_error(ctx, error):
    """Handle command errors with role restrictions"""
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(
            title="❌ Access Denied",
            description="You don't have permission to use this command.\n\nOnly users with the Management role can execute bot commands.",
            color=0xff0000
        )
        await ctx.send(embed=embed, delete_after=10)
        return

    if isinstance(error, commands.CommandNotFound):
        return  # Ignore command not found errors

    logger.error(f"Command error in {ctx.command}: {error}")
    try:
        await ctx.send("❌ An error occurred while processing your command.")
    except:
        pass


# ================= PREFIX COMMANDS WITH ROLE RESTRICTIONS =================
@bot.command(name="supportpanel")
@has_management_role()
async def supportpanel_cmd(ctx, create_order_panel: str = "false"):
    """Create the support ticket panel and optionally the order panel"""
    try:
        # Parse the create_order_panel argument
        create_order = create_order_panel.lower() in ['true', 'yes', '1', 'on']

        # Top banner embed
        top_embed = discord.Embed(color=0x2B2D31)
        top_embed.set_image(url=TOP_BANNER_URL)
        await ctx.send(embed=top_embed)

        # Main panel embed
        embed = discord.Embed(
            title="🎫 Support Ticket System",
            description="""
**Need help? We've got you covered!** 

Select the appropriate category below to create a support ticket:

🛠️ **Customer Support**
• Order-related concerns
• Product support & troubleshooting  
• Staff conduct reports
• Appeals for staff infractions
• General questions & assistance

⚙️ **Management**
• Partnership requests & inquiries
• Staff applications & resignations
• Perk claims & rewards
• Designer applications
• Moderation appeals

*Please choose the category that best matches your needs. Our team will respond as quickly as possible!*
            """,
            color=0x2B2D31
        )

        embed.set_image(url=BOTTOM_BANNER_URL)
        embed.set_footer(text="Use the dropdown below to create your ticket", icon_url=FOOTER_LOGO_URL)

        await ctx.send(embed=embed, view=TicketPanelView())

        # Create order panel if requested
        if create_order:
            # Top banner for orders
            order_banner_embed = discord.Embed(color=0x2B2D31)
            order_banner_embed.set_image(url=ORDER_BANNER_URL)
            await ctx.send(embed=order_banner_embed)

            # Main ordering panel
            order_embed = discord.Embed(
                title="🚨 ER:LC Design Services - Professional Quality",
                description="""
**Transform your Emergency Response: Liberty County experience!** 

Our professional design team specializes in high-quality, realistic designs for the ER:LC community. Choose from our range of services below:

🚗 **Liveries** - Custom vehicle skins & realistic fleet designs
👮 **Custom Uniforms** - Professional department uniforms & badges  
🚨 **ELS** - Emergency lighting system configurations
🤖 **Discord Services** - Complete server setup & management
⚙️ **Custom Bots** - Fully customized Discord bots for your server
➕ **More** - Additional services & custom requests

**Why choose us?**
• ✅ Professional quality guaranteed
• ✅ Fast turnaround times  
• ✅ Affordable Robux pricing
• ✅ Unlimited revisions included
• ✅ ER:LC specialists with years of experience

⚠️ **Important:** You can only have **1 active order at a time** to prevent spam and ensure quality service.

*Click a service button below to place your order and get started!*
                """,
                color=0x2B2D31
            )

            order_embed.add_field(
                name="💰 Payment & Process",
                value="All payments handled securely through Robux • Pricing discussed with designer • Work begins after payment • Full satisfaction guaranteed",
                inline=False
            )

            order_embed.set_image(url=ORDER_BOTTOM_URL)
            order_embed.set_footer(text="Professional ER:LC Design Services • Click below to order",
                                   icon_url=FOOTER_LOGO_URL)

            await ctx.send(embed=order_embed, view=OrderingPanelView())

    except Exception as e:
        logger.error(f"Error in supportpanel command: {e}")
        await ctx.send("❌ An error occurred while creating the panels.")


@bot.command(name="orderpanel")
@has_management_role()
async def orderpanel_cmd(ctx):
    """Create the professional ordering panel for ER:LC design services"""
    try:
        # Top banner
        banner_embed = discord.Embed(color=0x2B2D31)
        banner_embed.set_image(url=ORDER_BANNER_URL)
        await ctx.send(embed=banner_embed)

        # Main ordering panel
        embed = discord.Embed(
            title="🚨 ER:LC Design Services - Professional Quality",
            description="""
**Transform your Emergency Response: Liberty County experience!** 

Our professional design team specializes in high-quality, realistic designs for the ER:LC community. Choose from our range of services below:

🚗 **Liveries** - Custom vehicle skins & realistic fleet designs
👮 **Custom Uniforms** - Professional department uniforms & badges  
🚨 **ELS** - Emergency lighting system configurations
🤖 **Discord Services** - Complete server setup & management
⚙️ **Custom Bots** - Fully customized Discord bots for your server
➕ **More** - Additional services & custom requests

**Why choose us?**
• ✅ Professional quality guaranteed
• ✅ Fast turnaround times  
• ✅ Affordable Robux pricing
• ✅ Unlimited revisions included
• ✅ ER:LC specialists with years of experience

⚠️ **Important:** You can only have **1 active order at a time** to prevent spam and ensure quality service.

*Click a service button below to place your order and get started!*
            """,
            color=0x2B2D31
        )

        embed.add_field(
            name="💰 Payment & Process",
            value="All payments handled securely through Robux • Pricing discussed with designer • Work begins after payment • Full satisfaction guaranteed",
            inline=False
        )

        embed.set_image(url=ORDER_BOTTOM_URL)
        embed.set_footer(text="Professional ER:LC Design Services • Click below to order", icon_url=FOOTER_LOGO_URL)

        await ctx.send(embed=embed, view=OrderingPanelView())

    except Exception as e:
        logger.error(f"Error in orderpanel command: {e}")
        await ctx.send("❌ An error occurred while creating the order panel.")


@bot.command(name="welcomepanel")
@has_management_role()
async def welcomepanel_cmd(ctx):
    """Create a welcome panel with banner for testing"""
    try:
        # Send banner first
        if WELCOME_BANNER_URL:
            banner_embed = discord.Embed(color=0x2B2D31)
            banner_embed.set_image(url=WELCOME_BANNER_URL)
            await ctx.send(embed=banner_embed)

        # Then send welcome text below
        embed = discord.Embed(
            title="Welcome to CLA Designs!",
            description="Hope you enjoy your stay, feel free to order any time.",
            color=0x2B2D31
        )
        embed.add_field(
            name="Get Started",
            value="Please check out the Reaction Roles to keep yourself updated and engage with the community!",
            inline=False
        )
        embed.set_footer(text="CLA Designs • Professional ER:LC Design Services")
        embed.timestamp = discord.utils.utcnow()

        # No @everyone ping for testing
        await ctx.send("Hello 😎 🌟, welcome to CLA Designs.", embed=embed)

    except Exception as e:
        logger.error(f"Error in welcomepanel command: {e}")
        await ctx.send(f"❌ Error: {str(e)}")


@bot.command(name="welcomelive")
@has_management_role()
async def welcomelive_cmd(ctx):
    """Create a welcome panel with @everyone for live use"""
    try:
        # 1. Send hello message first
        await ctx.send("Hello @everyone 😎 🌟, welcome to CLA Designs.")

        # 2. Send banner second
        if WELCOME_BANNER_URL:
            banner_embed = discord.Embed(color=0x2B2D31)
            banner_embed.set_image(url=WELCOME_BANNER_URL)
            await ctx.send(embed=banner_embed)

        # 3. Send welcome info text last
        embed = discord.Embed(
            title="Welcome to CLA Designs!",
            description="Hope you enjoy your stay, feel free to order any time.",
            color=0x2B2D31
        )
        embed.add_field(
            name="Get Started",
            value="Please check out the Reaction Roles to keep yourself updated and engage with the community!",
            inline=False
        )
        embed.set_footer(text="CLA Designs • Professional ER:LC Design Services")
        embed.timestamp = discord.utils.utcnow()

        await ctx.send(embed=embed)

    except Exception as e:
        logger.error(f"Error in welcomelive command: {e}")
        await ctx.send(f"❌ Error: {str(e)}")


@bot.command(name="setwelcome")
@has_management_role()
async def setwelcome_cmd(ctx, channel: discord.TextChannel = None):
    """Set the welcome channel for new member messages"""
    try:
        if channel is None:
            channel = ctx.channel

        embed = discord.Embed(
            title="✅ Welcome Channel Set!",
            description=f"Welcome messages will now be sent to {channel.mention}\n\n**Channel ID:** {channel.id}\n\n*Note: Update WELCOME_CHANNEL_ID in the code with this ID for permanent configuration.*",
            color=0x00ff00
        )
        embed.add_field(
            name="Test Commands",
            value="• `.welcomepanel` - Test without @everyone ping\n• `.welcomelive` - Test with @everyone ping",
            inline=False
        )

        await ctx.send(embed=embed)

    except Exception as e:
        logger.error(f"Error in setwelcome command: {e}")
        await ctx.send("❌ An error occurred while setting the welcome channel.")


# ================= EVENTS =================
@bot.event
async def on_ready():
    print(f"🤖 Bot is online! Logged in as {bot.user}")
    print(f"📊 Connected to {len(bot.guilds)} guild(s)")

    # Add persistent views for support system
    bot.add_view(TicketPanelView())
    bot.add_view(TicketActionView())

    # Add persistent views for ordering system
    bot.add_view(OrderingPanelView())
    bot.add_view(OrderActionView())

    # Add persistent QC view
    bot.add_view(QCApprovalView("", "", "", None, None))

    # Add persistent payment verification view
    bot.add_view(PaymentVerificationView("", None, None))

    try:
        synced = await bot.tree.sync()
        print(f"🔄 Synced {len(synced)} slash command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")
        print(f"❌ Failed to sync commands: {e}")


@bot.event
async def on_error(event, *args, **kwargs):
    """Global error handler for bot events"""
    logger.error(f"Bot error in event {event}: {traceback.format_exc()}")


# ================= SLASH COMMANDS WITH ROLE RESTRICTIONS =================
@bot.tree.command(name="qc", description="Submit a product for Quality Control review")
@app_commands.describe(
    customer_username="The customer's username (Discord or Roblox)",
    product_type="Type of product (liveries, uniforms, etc.)",
    attachment="Upload the product file(s)",
    notes="Additional notes or comments (optional)"
)
async def quality_control(
        interaction: discord.Interaction,
        customer_username: str,
        product_type: str,
        attachment: discord.Attachment,
        notes: str = "No additional notes"
):
    """Submit a product for Quality Control review"""
    try:
        # Check if user is a designer
        designer_role = interaction.guild.get_role(DESIGNER_ROLE_ID)
        if not designer_role or designer_role not in interaction.user.roles:
            await interaction.response.send_message("❌ Only designers can submit products for QC.", ephemeral=True)
            return

        # Find the order channel and customer by username
        order_channel, customer = find_order_channel_by_customer(interaction.guild, customer_username)

        # If not found by channel search, try to find customer by username
        if not customer:
            customer = get_customer_from_username(interaction.guild, customer_username)

        # Get QC channel
        qc_channel = interaction.guild.get_channel(QC_CHANNEL_ID)
        if not qc_channel:
            await interaction.response.send_message("❌ QC channel not found. Please check the configuration.",
                                                    ephemeral=True)
            return

        # Create QC submission embed
        embed = discord.Embed(
            title="🔍 Quality Control Submission",
            description=f"Product for **{customer_username}** is ready for quality review!",
            color=0xffaa00
        )
        embed.add_field(name="👤 Customer",
                        value=f"{customer_username}\n{customer.mention if customer else 'Not found in server'}",
                        inline=True)
        embed.add_field(name="📦 Product Type", value=product_type, inline=True)
        embed.add_field(name="🎨 Designer", value=interaction.user.mention, inline=True)
        embed.add_field(name="🔗 Order Channel", value=order_channel.mention if order_channel else "Not found",
                        inline=True)
        embed.add_field(name="📝 Notes", value=notes, inline=False)
        embed.add_field(name="📎 Attachment", value=f"[{attachment.filename}]({attachment.url})", inline=False)

        embed.set_footer(text="QC Team: Please review and approve/deny this submission", icon_url=FOOTER_LOGO_URL)
        embed.timestamp = discord.utils.utcnow()

        # Send to QC channel with approval buttons
        qc_view = QCApprovalView(customer_username, product_type, notes, interaction.user, order_channel)
        qc_message = await qc_channel.send(embed=embed, view=qc_view)

        # Also send the attachment file
        await qc_channel.send(file=await attachment.to_file())

        # Confirm submission to designer
        success_embed = discord.Embed(
            title="✅ QC Submission Successful",
            description=f"Your product for **{customer_username}** has been submitted for quality control review.",
            color=0x00ff00
        )
        success_embed.add_field(name="Customer",
                                value=f"{customer_username} ({customer.mention if customer else 'Not in server'})",
                                inline=True)
        success_embed.add_field(name="Product Type", value=product_type, inline=True)
        success_embed.add_field(name="QC Message", value=f"[View Submission]({qc_message.jump_url})", inline=True)
        success_embed.add_field(name="Status", value="⏳ Pending Review", inline=False)

        await interaction.response.send_message(embed=success_embed, ephemeral=True)

    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to send messages to the QC channel.",
                                                ephemeral=True)
    except Exception as e:
        logger.error(f"Error in QC command: {e}")
        await interaction.response.send_message(f"❌ An error occurred while submitting to QC.", ephemeral=True)


@bot.tree.command(name="payment-proof", description="Submit payment proof for an order")
@app_commands.describe(
    customer_username="The customer's username (Discord or Roblox)",
    payment_screenshot="Upload screenshot/proof of payment"
)
async def payment_proof(
        interaction: discord.Interaction,
        customer_username: str,
        payment_screenshot: discord.Attachment
):
    """Submit payment proof for an order"""
    try:
        # Find the order channel and customer by username
        order_channel, customer = find_order_channel_by_customer(interaction.guild, customer_username)

        # If not found by channel search, try to find customer by username
        if not customer:
            customer = get_customer_from_username(interaction.guild, customer_username)

        # Check if the user is the customer or has management role
        management_role = interaction.guild.get_role(MANAGEMENT_ROLE_ID)
        is_customer = customer and interaction.user.id == customer.id
        is_management = management_role and management_role in interaction.user.roles
        is_designer = interaction.guild.get_role(DESIGNER_ROLE_ID) and interaction.guild.get_role(
            DESIGNER_ROLE_ID) in interaction.user.roles

        if not (is_customer or is_management or is_designer):
            await interaction.response.send_message(
                "❌ You can only submit payment proof for your own orders or if you're staff.",
                ephemeral=True
            )
            return

        # Get payment proof channel
        payment_channel = interaction.guild.get_channel(PAYMENT_PROOF_CHANNEL_ID)
        if not payment_channel:
            await interaction.response.send_message(
                "❌ Payment proof channel not found. Please contact an administrator.",
                ephemeral=True
            )
            return

        # Create payment proof embed
        embed = discord.Embed(
            title="💰 Payment Proof Submitted",
            description=f"Payment proof for **{customer_username}** received!",
            color=0x00aa00
        )
        embed.add_field(name="👤 Customer",
                        value=f"{customer_username}\n{customer.mention if customer else 'Not found in server'}",
                        inline=True)
        embed.add_field(name="📋 Submitted By", value=interaction.user.mention, inline=True)
        embed.add_field(name="🔗 Order Channel", value=order_channel.mention if order_channel else "Not found",
                        inline=True)
        embed.add_field(name="📎 Payment Screenshot", value=f"[{payment_screenshot.filename}]({payment_screenshot.url})",
                        inline=False)

        embed.set_footer(text="Management: Please verify this payment", icon_url=FOOTER_LOGO_URL)
        embed.timestamp = discord.utils.utcnow()

        # Send to payment proof channel
        payment_view = PaymentVerificationView(customer_username, customer, order_channel)
        payment_message = await payment_channel.send(embed=embed, view=payment_view)

        # Also send the payment screenshot
        await payment_channel.send(file=await payment_screenshot.to_file())

        # Send confirmation to order channel
        if order_channel:
            try:
                payment_confirmation = discord.Embed(
                    title="💰 Payment Proof Submitted",
                    description=f"Payment proof has been submitted for **{customer_username}**!",
                    color=0x00aa00
                )
                payment_confirmation.add_field(name="Status", value="⏳ Pending Verification", inline=True)
                payment_confirmation.add_field(name="Next Steps", value="Management will verify the payment shortly.",
                                               inline=False)
                payment_confirmation.set_footer(text="Thank you for your payment!", icon_url=FOOTER_LOGO_URL)

                await order_channel.send(embed=payment_confirmation)
            except Exception as e:
                logger.error(f"Error sending payment confirmation to order channel: {e}")

        # Confirm submission to user
        success_embed = discord.Embed(
            title="✅ Payment Proof Submitted Successfully",
            description=f"Payment proof for **{customer_username}** has been submitted for verification.",
            color=0x00ff00
        )
        success_embed.add_field(name="Order Channel", value=order_channel.mention if order_channel else "Not found",
                                inline=True)
        success_embed.add_field(name="Status", value="⏳ Pending Verification", inline=True)
        success_embed.add_field(name="Payment Review", value=f"[View Submission]({payment_message.jump_url})",
                                inline=True)

        await interaction.response.send_message(embed=success_embed, ephemeral=True)

    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to send messages to the payment channel.",
                                                ephemeral=True)
    except Exception as e:
        logger.error(f"Error in payment proof command: {e}")
        await interaction.response.send_message("❌ An error occurred while submitting payment proof.", ephemeral=True)


@bot.tree.command(name="receipt", description="Generate a professional receipt for completed orders")
async def generate_receipt(interaction: discord.Interaction):
    """Generate a receipt for a completed order"""
    try:
        # Check if user is a designer or management
        designer_role = interaction.guild.get_role(DESIGNER_ROLE_ID)
        management_role = interaction.guild.get_role(MANAGEMENT_ROLE_ID)

        if not ((designer_role and designer_role in interaction.user.roles) or
                (management_role and management_role in interaction.user.roles)):
            await interaction.response.send_message("❌ Only designers and management can generate receipts.",
                                                    ephemeral=True)
            return

        # Show the receipt modal
        modal = ReceiptModal()
        await interaction.response.send_modal(modal)

    except Exception as e:
        logger.error(f"Error in receipt command: {e}")
        await interaction.response.send_message("❌ An error occurred while generating the receipt.", ephemeral=True)


@bot.tree.command(name="ping", description="Check bot latency and status")
async def ping(interaction: discord.Interaction):
    """Check bot latency and status"""
    try:
        # Check if user has management role
        if not check_management_role_interaction(interaction):
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You don't have permission to use this command.\n\nOnly users with the Management role can execute bot commands.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        latency = round(bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot latency: **{latency}ms**",
            color=0x00ff00 if latency < 100 else 0xffaa00 if latency < 200 else 0xff0000
        )
        embed.add_field(name="Status", value="✅ Online and operational", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        logger.error(f"Error in ping command: {e}")
        await interaction.response.send_message("❌ An error occurred while checking latency.", ephemeral=True)


@bot.tree.command(name="unclaim", description="Unclaim an order (Designers only)")
@app_commands.describe(
    customer_username="The customer's username to find their order"
)
async def unclaim_order(interaction: discord.Interaction, customer_username: str):
    """Unclaim an order and reset channel name"""
    try:
        # Check if user is a designer
        designer_role = interaction.guild.get_role(DESIGNER_ROLE_ID)
        if not designer_role or designer_role not in interaction.user.roles:
            await interaction.response.send_message("❌ Only designers can unclaim orders.", ephemeral=True)
            return

        # Find the order channel and customer
        order_channel, customer = find_order_channel_by_customer(interaction.guild, customer_username)

        if not order_channel:
            await interaction.response.send_message(
                f"❌ **Order for {customer_username} not found!**\n\n"
                f"Please ensure:\n"
                f"• The customer username is correct\n"
                f"• The order channel still exists",
                ephemeral=True
            )
            return

        # Check if the current user claimed this order (by checking if their name is in the channel name)
        if interaction.user.display_name.lower().replace(' ', '-').replace(':', '') not in order_channel.name.lower():
            await interaction.response.send_message(
                f"❌ You haven't claimed the order for {customer_username} or someone else claimed it.",
                ephemeral=True
            )
            return

        # Get service type from channel topic or name
        service_type = "order"  # default
        if order_channel.topic:
            topic_parts = order_channel.topic.split()
            for part in topic_parts:
                if "liveries" in part.lower():
                    service_type = "liveries"
                    break
                elif "uniform" in part.lower():
                    service_type = "custom-uniforms"
                    break
                elif "els" in part.lower():
                    service_type = "els"
                    break
                elif "discord" in part.lower():
                    service_type = "discord-services"
                    break
                elif "bot" in part.lower():
                    service_type = "custom-bots"
                    break
                elif "more" in part.lower() or "additional" in part.lower():
                    service_type = "more"
                    break

        # Extract order number from channel name if possible
        import re
        order_match = re.search(r'-(\d+)-', order_channel.name)
        order_number = order_match.group(1) if order_match else "000"

        # Reset channel name to original format (remove designer name and green emoji)
        try:
            customer_name = customer.display_name if customer else customer_username
            new_channel_name = f"{service_type}-{order_number}-{customer_name}".replace(' ', '-').replace(':', '')
            await order_channel.edit(name=new_channel_name)
        except Exception as e:
            logger.error(f"Error updating channel name: {e}")

        # Send unclaim notification
        embed = discord.Embed(
            title="🔄 Order Unclaimed",
            description=f"Order for **{customer_username}** has been unclaimed by {interaction.user.mention}",
            color=0xffa500
        )
        embed.add_field(name="Status", value="🟡 Waiting for Designer", inline=True)
        embed.add_field(name="Customer", value=customer.mention if customer else customer_username, inline=True)
        embed.add_field(name="Next Steps", value="This order is now available for other designers to claim.",
                        inline=False)

        await interaction.response.send_message(embed=embed)

    except Exception as e:
        logger.error(f"Error in unclaim command: {e}")
        await interaction.response.send_message("❌ An error occurred while unclaiming the order.", ephemeral=True)


@bot.tree.command(name="cleanup", description="Clean up old/broken tickets and orders (Management only)")
async def cleanup(interaction: discord.Interaction):
    """Clean up old/broken tickets and orders"""
    try:
        # Check if user has management role
        if not check_management_role_interaction(interaction):
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You don't have permission to use this command.\n\nOnly users with the Management role can execute bot commands.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        guild = interaction.guild
        cleaned_channels = []

        # Check ticket categories
        ticket_categories = [TICKET_CATEGORY_ID_CUSTOMER, TICKET_CATEGORY_ID_MANAGEMENT]
        order_categories = [
            LIVERIES_CATEGORY_ID, UNIFORMS_CATEGORY_ID, ELS_CATEGORY_ID,
            DISCORD_SERVICES_CATEGORY_ID, CUSTOM_BOTS_CATEGORY_ID, MORE_CATEGORY_ID
        ]

        all_categories = ticket_categories + order_categories

        for category_id in all_categories:
            category = guild.get_channel(category_id)
            if category and isinstance(category, discord.CategoryChannel):
                for channel in category.channels:
                    if isinstance(channel, discord.TextChannel):
                        # Check if channel has any recent messages (last 7 days)
                        try:
                            async for message in channel.history(limit=1,
                                                                 after=discord.utils.utcnow() - discord.utils.timedelta(
                                                                     days=7)):
                                break
                            else:
                                # No recent messages, mark for cleanup
                                cleaned_channels.append(channel.name)
                        except:
                            continue

        embed = discord.Embed(
            title="🧹 Cleanup Report",
            description=f"Found **{len(cleaned_channels)}** potentially inactive channels.",
            color=0xffaa00
        )

        if cleaned_channels:
            embed.add_field(
                name="Inactive Channels",
                value="\n".join(cleaned_channels[:10]) + ("..." if len(cleaned_channels) > 10 else ""),
                inline=False
            )
            embed.add_field(
                name="⚠️ Note",
                value="This is a report only. To actually delete inactive channels, you'll need to do it manually or implement auto-cleanup.",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    except Exception as e:
        logger.error(f"Error in cleanup command: {e}")
        await interaction.response.send_message("❌ An error occurred during cleanup.", ephemeral=True)

@bot.tree.command(name="dm", description="Send a direct message to a user (Management only)")
@app_commands.describe(
    user="The user to send a message to",
    message="The message to send"
)
async def dm_user(interaction: discord.Interaction, user: discord.Member, message: str):
    """Send a direct message to a specified user"""
    try:
        # Check if user has management role
        if not check_management_role_interaction(interaction):
            await interaction.response.send_message(
                "❌ You don’t have permission to use this command.\n"
                "Only Management can send DM commands.\n\n"
                "_Open a support ticket for any enquiries._",
                ephemeral=True
            )
            return

        # Message text (no staff name or role shown)
        dm_text = (
            f"📩 **Message from CLA Designs Staff**\n\n"
            f"{message}\n\n"
            f"_Open a support ticket for any enquiries._"
        )

        # Try to send the DM
        try:
            await user.send(dm_text)

            await interaction.response.send_message(
                f"✅ Message successfully sent to {user.mention}.\n\n"
                f"**Message Preview:**\n{message[:100] + ('...' if len(message) > 100 else '')}\n\n"
                "_Open a support ticket for any enquiries._",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                f"❌ Could not send DM to {user.mention}. They may have DMs disabled or blocked the bot.\n\n"
                "_Open a support ticket for any enquiries._",
                ephemeral=True
            )

    except Exception as e:
        logger.error(f"Error in DM command: {e}")
        await interaction.response.send_message(
            "❌ An error occurred while sending the DM.\n\n"
            "_Open a support ticket for any enquiries._",
            ephemeral=True
        )


# Add this at the top of your file with other imports
from datetime import datetime, timedelta

# Add this near your other global variables (after the config section)
# Dictionary to track last purge time per channel
purge_cooldowns = {}


# Add this prefix command with your other prefix commands
@bot.command(name="purge")
@has_management_role()
async def purge_messages(ctx, amount: int = None):
    """Purge messages from the current channel (Management only, max 15, 2 hour cooldown)"""
    try:
        # Check if amount is provided
        if amount is None:
            embed = discord.Embed(
                title="❌ Missing Amount",
                description="Please specify the number of messages to purge.\n\n**Usage:** `.purge <number>`\n**Example:** `.purge 10`",
                color=0xff0000
            )
            await ctx.send(embed=embed, delete_after=10)
            return

        # Validate amount (max 15 messages)
        if amount < 1 or amount > 15:
            embed = discord.Embed(
                title="❌ Invalid Amount",
                description="Please specify a number between **1** and **15** messages.",
                color=0xff0000
            )
            await ctx.send(embed=embed, delete_after=10)
            return

        # Check cooldown (2 hours per channel)
        channel_id = ctx.channel.id
        current_time = datetime.utcnow()
        cooldown_duration = timedelta(hours=2)

        if channel_id in purge_cooldowns:
            last_purge = purge_cooldowns[channel_id]
            time_left = (last_purge + cooldown_duration) - current_time

            if time_left.total_seconds() > 0:
                hours = int(time_left.total_seconds() // 3600)
                minutes = int((time_left.total_seconds() % 3600) // 60)

                embed = discord.Embed(
                    title="⏰ Cooldown Active",
                    description=f"Purge command is on cooldown for this channel.\n\n**Time remaining:** {hours}h {minutes}m",
                    color=0xffaa00
                )
                await ctx.send(embed=embed, delete_after=15)
                return

        # Check bot permissions
        if not ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="I don't have permission to delete messages in this channel.\n\nRequired permission: **Manage Messages**",
                color=0xff0000
            )
            await ctx.send(embed=embed, delete_after=10)
            return

        # Send confirmation message
        confirm_embed = discord.Embed(
            title="🗑️ Purging Messages",
            description=f"Deleting {amount} messages from {ctx.channel.mention}...",
            color=0xffaa00
        )
        status_msg = await ctx.send(embed=confirm_embed)

        # Delete messages (excluding the command message and status message)
        deleted = await ctx.channel.purge(
            limit=amount + 1,  # +1 to account for the command message
            check=lambda m: m.id != status_msg.id  # Don't delete the status message
        )

        # Update cooldown
        purge_cooldowns[channel_id] = current_time

        # Send success message
        success_embed = discord.Embed(
            title="✅ Messages Purged",
            description=f"Successfully deleted **{len(deleted) - 1}** messages from {ctx.channel.mention}",
            color=0x00ff00
        )
        success_embed.add_field(
            name="Executed by",
            value=ctx.author.mention,
            inline=True
        )
        success_embed.add_field(
            name="Next purge available",
            value=f"<t:{int((current_time + cooldown_duration).timestamp())}:R>",
            inline=True
        )
        success_embed.set_footer(text="This message will be deleted in 10 seconds")

        # Edit the status message to show success
        await status_msg.edit(embed=success_embed, delete_after=10)

    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ Permission Error",
            description="I don't have permission to delete messages in this channel.",
            color=0xff0000
        )
        await ctx.send(embed=embed, delete_after=10)
    except Exception as e:
        logger.error(f"Error in purge command: {e}")
        embed = discord.Embed(
            title="❌ Error",
            description="An error occurred while trying to purge messages.",
            color=0xff0000
        )
        await ctx.send(embed=embed, delete_after=10)


@bot.tree.command(name="tax", description="Calculate Roblox tax (30%) on any amount")
@app_commands.describe(
    amount="The amount of Robux before tax"
)
async def calculate_tax(interaction: discord.Interaction, amount: int):
    """Calculate Roblox tax and show how much you'll receive"""
    try:
        # Validate amount
        if amount < 1:
            await interaction.response.send_message("❌ Please enter a valid Robux amount (must be positive).",
                                                    ephemeral=True)
            return

        # Calculate tax (30%)
        tax_rate = 0.30
        tax_amount = int(amount * tax_rate)
        amount_after_tax = amount - tax_amount

        # Create embed
        embed = discord.Embed(
            title="💰 Roblox Tax Calculator",
            description="Roblox takes a 30% tax on all transactions",
            color=0x00ff00
        )

        embed.add_field(
            name="💵 Amount Before Tax",
            value=f"**R$ {amount:,}**",
            inline=True
        )

        embed.add_field(
            name="📊 Tax (30%)",
            value=f"**-R$ {tax_amount:,}**",
            inline=True
        )

        embed.add_field(
            name="✅ You Receive",
            value=f"**R$ {amount_after_tax:,}**",
            inline=True
        )

        embed.set_footer(text="CLA Designs • Tax Calculator", icon_url=FOOTER_LOGO_URL)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    except Exception as e:
        logger.error(f"Error in tax command: {e}")
        await interaction.response.send_message("❌ An error occurred while calculating tax.", ephemeral=True)

@bot.tree.command(name="infraction", description="Log a staff infraction (Management only)")
@app_commands.describe(
    user="The staff member receiving the infraction",
    punishment="Type of punishment (Warning, Suspension, Termination, etc.)",
    reason="Reason for the infraction",
    notes="Additional notes (optional)"
)
@app_commands.choices(punishment=[
    app_commands.Choice(name="Warning", value="Warning"),
    app_commands.Choice(name="Suspension", value="Suspension"),
    app_commands.Choice(name="Termination", value="Termination"),
    app_commands.Choice(name="Demotion", value="Demotion"),
    app_commands.Choice(name="Strike", value="Strike")
])
async def infraction(
    interaction: discord.Interaction,
    user: discord.Member,
    punishment: str,
    reason: str,
    notes: str = "N/A"
):
    """Log a staff infraction"""
    try:
        # Check if user has management role
        if not check_management_role_interaction(interaction):
            await interaction.response.send_message(
                "❌ Only Management can issue infractions.",
                ephemeral=True
            )
            return

        # Get infraction channel
        infraction_channel = interaction.guild.get_channel(INFRACTION_CHANNEL_ID)
        if not infraction_channel:
            await interaction.response.send_message(
                "❌ Infraction channel not found. Please contact an administrator.",
                ephemeral=True
            )
            return

        # Get current timestamp
        timestamp = discord.utils.format_dt(discord.utils.utcnow(), style='F')
        timestamp_short = discord.utils.format_dt(discord.utils.utcnow(), style='f')

        # Create infraction banner embed
        banner_embed = discord.Embed(color=0xED4245)  # Discord red color
        banner_embed.set_image(url=INFRACTION_BANNER_URL)

        # Create main infraction embed
        infraction_embed = discord.Embed(
            title=f"Signed, {interaction.user.display_name}",
            description="",
            color=0xED4245
        )

        # Add infraction details
        infraction_content = f"""**User Infraction Logged**

**User**
{user.mention}

**Punishment**
{punishment}

**Reason**
{reason}

**Notes**
{notes}
"""
        infraction_embed.description = infraction_content
        infraction_embed.timestamp = discord.utils.utcnow()

        # Send to infraction channel
        await infraction_channel.send(content=user.mention, embeds=[banner_embed, infraction_embed])

        # Try to DM the staff member
        try:
            dm_embed = discord.Embed(
                title="⚠️ Staff Infraction Notice",
                description=f"You have received an infraction from **CLA Designs Management**.",
                color=0xED4245
            )
            dm_embed.add_field(name="Punishment", value=punishment, inline=True)
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Notes", value=notes, inline=False)
            dm_embed.add_field(name="Issued By", value=interaction.user.mention, inline=True)
            dm_embed.set_footer(text="CLA Designs • Staff Management", icon_url=FOOTER_LOGO_URL)
            dm_embed.timestamp = discord.utils.utcnow()

            await user.send(embed=dm_embed)
            dm_status = "✅ DM sent successfully"
        except discord.Forbidden:
            dm_status = "⚠️ Could not send DM (user has DMs disabled)"
        except Exception as e:
            logger.error(f"Error sending infraction DM: {e}")
            dm_status = "⚠️ Could not send DM"

        # Confirm to management
        success_embed = discord.Embed(
            title="✅ Infraction Logged",
            description=f"Infraction for {user.mention} has been logged successfully.",
            color=0x00ff00
        )
        success_embed.add_field(name="Punishment", value=punishment, inline=True)
        success_embed.add_field(name="DM Status", value=dm_status, inline=True)

        await interaction.response.send_message(embed=success_embed, ephemeral=True)

    except Exception as e:
        logger.error(f"Error in infraction command: {e}")
        await interaction.response.send_message("❌ An error occurred while logging the infraction.", ephemeral=True)


@bot.tree.command(name="promotion", description="Announce a staff promotion (Management only)")
@app_commands.describe(
    user="The staff member being promoted",
    new_role="Their new role/position",
    message="Congratulatory message (optional)"
)
async def promotion(
    interaction: discord.Interaction,
    user: discord.Member,
    new_role: str,
    message: str = "Congratulations on your well-deserved promotion! Keep up the great work! 🎉"
):
    """Announce a staff promotion"""
    try:
        # Check if user has management role
        if not check_management_role_interaction(interaction):
            await interaction.response.send_message(
                "❌ Only Management can announce promotions.",
                ephemeral=True
            )
            return

        # Get promotion channel
        promotion_channel = interaction.guild.get_channel(PROMOTION_CHANNEL_ID)
        if not promotion_channel:
            await interaction.response.send_message(
                "❌ Promotion channel not found. Please contact an administrator.",
                ephemeral=True
            )
            return

        # Create promotion banner embed
        banner_embed = discord.Embed(color=0x57F287)  # Discord green color
        banner_embed.set_image(url=PROMOTION_BANNER_URL)

        # Create main promotion embed
        promotion_embed = discord.Embed(
            title=f"Signed, {interaction.user.display_name}",
            description="",
            color=0x57F287
        )

        # Add promotion details
        promotion_content = f"""**Staff Promotion Announcement**

**User**
{user.mention}

**New Position**
{new_role}

**Message**
{message}

**Promoted By**
{interaction.user.mention}
"""
        promotion_embed.description = promotion_content
        promotion_embed.timestamp = discord.utils.utcnow()
        promotion_embed.set_footer(text="CLA Designs • Staff Management", icon_url=FOOTER_LOGO_URL)

        # Send to promotion channel
        await promotion_channel.send(content=f"🎉 {user.mention}", embeds=[banner_embed, promotion_embed])

        # Try to DM the staff member
        try:
            dm_embed = discord.Embed(
                title="🎉 Congratulations on Your Promotion!",
                description=f"You have been promoted at **CLA Designs**!",
                color=0x57F287
            )
            dm_embed.add_field(name="New Position", value=new_role, inline=True)
            dm_embed.add_field(name="Promoted By", value=interaction.user.mention, inline=True)
            dm_embed.add_field(name="Message", value=message, inline=False)
            dm_embed.set_footer(text="CLA Designs • Congratulations!", icon_url=FOOTER_LOGO_URL)
            dm_embed.timestamp = discord.utils.utcnow()

            await user.send(embed=dm_embed)
            dm_status = "✅ DM sent successfully"
        except discord.Forbidden:
            dm_status = "⚠️ Could not send DM (user has DMs disabled)"
        except Exception as e:
            logger.error(f"Error sending promotion DM: {e}")
            dm_status = "⚠️ Could not send DM"

        # Confirm to management
        success_embed = discord.Embed(
            title="✅ Promotion Announced",
            description=f"Promotion for {user.mention} has been announced successfully.",
            color=0x00ff00
        )
        success_embed.add_field(name="New Role", value=new_role, inline=True)
        success_embed.add_field(name="DM Status", value=dm_status, inline=True)

        await interaction.response.send_message(embed=success_embed, ephemeral=True)

    except Exception as e:
        logger.error(f"Error in promotion command: {e}")
        await interaction.response.send_message("❌ An error occurred while announcing the promotion.", ephemeral=True)

# ================= RUN BOT =================
if __name__ == "__main__":
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables!")
        print("❌ DISCORD_TOKEN not found! Please check your .env file.")
        exit(1)

    try:
        bot.run(token)
    except discord.LoginFailure:
        logger.error("Invalid Discord token!")
        print("❌ Invalid Discord token! Please check your .env file.")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        print(f"❌ Failed to start bot: {e}")