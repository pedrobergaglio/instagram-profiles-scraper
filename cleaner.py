import pandas as pd

def clean_data(df):
    # Sort by column: 'account_type' (descending)
    df = df.sort_values(['account_type'], ascending=[False])
    # Drop columns: 'can_hide_category', 'primary_profile_link_type' and 31 other columns
    df = df.drop(columns=['can_hide_category', 'primary_profile_link_type', 'show_fb_link_on_profile', 'show_fb_page_link_on_profile', 'ads_page_id', 'ads_page_name', 'current_catalog_id', 'mini_shop_seller_onboarding_status', 'ads_incentive_expiration_date', 'account_category', 'can_add_fb_group_link_on_profile', 'can_use_affiliate_partnership_messaging_as_creator', 'can_use_affiliate_partnership_messaging_as_brand', 'existing_user_age_collection_enabled', 'fbid_v2', 'feed_post_reshare_disabled', 'has_guides', 'has_ig_profile', 'has_public_tab_threads', 'highlight_reshare_disabled', 'highlights_tray_type', 'include_direct_blacklist_status', 'is_direct_roll_call_enabled', 'is_eligible_for_post_boost_mv_upsell', 'is_meta_verified_related_accounts_display_enabled', 'is_eligible_for_meta_verified_links_in_reels', 'is_eligible_for_meta_verified_label', 'is_new_to_instagram', 'is_parenting_account', 'is_private', 'is_profile_broadcast_sharing_enabled', 'is_recon_ad_cta_on_profile_eligible_with_viewer', 'is_secondary_account_creation'])
    # Drop column: 'is_eligible_for_lead_center'
    df = df.drop(columns=['is_eligible_for_lead_center'])
    # Filter rows where external_url, contact_phone_number, or public_phone_number are not empty
    df = df[(df['external_url'].notna()) | (df['contact_phone_number'].notna()) | (df['public_phone_number'].notna())]
    # Drop columns: 'is_opal_enabled', 'strong_id__', 'has_ever_selected_topics'
    df = df.drop(columns=['is_opal_enabled', 'strong_id__', 'has_ever_selected_topics'])
    # Drop columns: 'third_party_downloads_enabled', 'recon_features' and 2 other columns
    df = df.drop(columns=['third_party_downloads_enabled', 'recon_features', 'show_account_transparency_details', 'show_post_insights_entry_point'])
    # Drop columns: 'has_gen_ai_personas_for_profile_banner', 'has_nme_badge' and 2 other columns
    df = df.drop(columns=['has_gen_ai_personas_for_profile_banner', 'has_nme_badge', 'pk', 'pk_id'])
    # Drop columns: 'is_auto_confirm_enabled_for_all_reciprocal_follow_requests', 'is_active_on_text_post_app' and 2 other columns
    df = df.drop(columns=['is_auto_confirm_enabled_for_all_reciprocal_follow_requests', 'is_active_on_text_post_app', 'views_on_grid_status', 'id'])
    # Drop columns: 'has_biography_translation', 'can_hide_public_contacts'
    df = df.drop(columns=['has_biography_translation', 'can_hide_public_contacts'])
    # Drop columns: 'is_category_tappable', 'should_show_public_contacts', 'is_eligible_for_smb_support_flow'
    df = df.drop(columns=['is_category_tappable', 'should_show_public_contacts', 'is_eligible_for_smb_support_flow'])
    # Drop columns: 'professional_conversion_suggested_account_type', 'direct_messaging' and 2 other columns
    df = df.drop(columns=['professional_conversion_suggested_account_type', 'direct_messaging', 'fb_page_call_to_action_id', 'instagram_location_id'])
    # Drop column: 'city_id'
    df = df.drop(columns=['city_id'])
    # Drop columns: 'is_profile_audio_call_enabled', 'latitude', 'longitude'
    df = df.drop(columns=['is_profile_audio_call_enabled', 'latitude', 'longitude'])
    # Drop columns: 'displayed_action_button_partner', 'smb_delivery_partner' and 6 other columns
    df = df.drop(columns=['displayed_action_button_partner', 'smb_delivery_partner', 'smb_support_delivery_partner', 'displayed_action_button_type', 'smb_support_partner', 'is_call_to_action_enabled', 'num_of_admined_pages', 'page_id'])
    # Drop columns: 'shopping_post_onboard_nux_type', 'account_badges' and 2 other columns
    df = df.drop(columns=['shopping_post_onboard_nux_type', 'account_badges', 'additional_business_addresses', 'auto_expand_chaining'])
    # Drop columns: 'enable_add_school_in_edit_profile', 'birthday_today_visibility_for_viewer' and 4 other columns
    df = df.drop(columns=['enable_add_school_in_edit_profile', 'birthday_today_visibility_for_viewer', 'can_use_branded_content_discovery_as_brand', 'can_use_branded_content_discovery_as_creator', 'can_use_paid_partnership_messaging_as_creator', 'chaining_upsell_cards'])
    # Drop columns: 'fan_club_info', 'follow_friction_type' and 4 other columns
    df = df.drop(columns=['fan_club_info', 'follow_friction_type', 'follower_count', 'following_count', 'has_anonymous_profile_picture', 'has_chaining'])
    # Drop columns: 'has_chains', 'has_exclusive_feed_content' and 6 other columns
    df = df.drop(columns=['has_chains', 'has_exclusive_feed_content', 'has_fan_club_subscriptions', 'has_highlight_reels', 'has_legacy_bb_pending_profile_picture_update', 'has_music_on_profile', 'has_mv4b_pending_profile_picture_update', 'has_private_collections'])
    # Drop columns: 'interop_messaging_user_fbid', 'instagram_pk' and 24 other columns
    df = df.drop(columns=['interop_messaging_user_fbid', 'instagram_pk', 'is_bestie', 'is_creator_agent_enabled', 'meta_verified_benefits_info', 'is_eligible_for_meta_verified_enhanced_link_sheet', 'is_eligible_for_meta_verified_enhanced_link_sheet_consumption', 'is_eligible_for_meta_verified_multiple_addresses_creation', 'is_eligible_for_meta_verified_multiple_addresses_consumption', 'is_eligible_for_meta_verified_related_accounts', 'is_legacy_verified_max_profile_pic_edit_reached', 'is_mv4b_application_matured_for_profile_edit', 'is_mv4b_biz_asset_profile_locked', 'is_mv4b_max_profile_edit_reached', 'meta_verified_related_accounts_count', 'is_favorite', 'is_in_canada', 'is_interest_account', 'is_memorialized', 'is_potential_business', 'is_regulated_news_in_viewer_location', 'is_remix_setting_enabled_for_posts', 'is_remix_setting_enabled_for_reels', 'is_regulated_c18', 'is_stories_teaser_muted', 'is_supervision_features_enabled'])
    # Drop column: 'latest_besties_reel_media'
    df = df.drop(columns=['latest_besties_reel_media'])
    # Drop column: 'live_subscription_status'
    df = df.drop(columns=['live_subscription_status'])
    # Drop columns: 'nametag', 'not_meta_verified_friction_info' and 15 other columns
    df = df.drop(columns=['nametag', 'not_meta_verified_friction_info', 'open_external_url_with_in_app_browser', 'pinned_channels_info', 'profile_context', 'profile_context_facepile_users', 'profile_context_links_with_user_ids', 'profile_pic_id', 'profile_pic_url', 'pronouns', 'relevant_news_regulation_locations', 'remove_message_entrypoint', 'show_blue_badge_on_main_profile', 'show_schools_badge', 'spam_follower_setting_enabled', 'text_app_last_visited_time', 'total_ar_effects'])
    # Drop columns: 'transparency_product_enabled', 'is_profile_picture_expansion_enabled' and 17 other columns
    df = df.drop(columns=['transparency_product_enabled', 'is_profile_picture_expansion_enabled', 'recs_from_friends', 'adjusted_banners_order', 'is_eligible_for_request_message', 'is_open_to_collab', 'is_oregon_custom_gender_consented', 'profile_reels_sorting_eligibility', 'nonpro_can_maybe_see_profile_hypercard', 'chaining_results', 'chaining_suggestions', 'has_igtv_series', 'show_ig_app_switcher_badge', 'show_text_post_app_switcher_badge', 'show_text_post_app_badge', 'text_post_app_joiner_number', 'text_post_app_joiner_number_label', 'text_post_app_badge_label', 'text_post_new_post_count'])
    # Drop column: 'total_igtv_videos'
    df = df.drop(columns=['total_igtv_videos'])
    # Drop columns: 'meta_verified_related_accounts_info', 'account_warning'
    df = df.drop(columns=['meta_verified_related_accounts_info', 'account_warning'])
    return df

# Loaded variable 'df' from URI: /Users/pedrobergaglio/2023/instagram-scraper/data/followers_detailed_elviejowatt_20250225_012321.csv
df = pd.read_csv(r'/Users/pedrobergaglio/2023/instagram-scraper/data/followers_detailed_elviejowatt_20250225_012321.csv')

df_clean = clean_data(df.copy())
df_clean.head()